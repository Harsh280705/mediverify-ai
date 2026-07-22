from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from services.doctor_monitoring import DoctorMonitoringService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
monitoring_service = DoctorMonitoringService()

@router.get("/alerts")
def get_alerts(current_user: dict = Depends(get_current_user)):
    role = current_user.get("role")
    uid = current_user.get("uid")
    
    if role not in ["doctor", "caregiver"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors and caregivers can access alerts."
        )
        
    # Get user document properties
    linked_field = "assignedPatients" if role == "doctor" else "linkedPatients"
    linked_patients = current_user.get(linked_field, [])
    
    if not linked_patients:
        return []
        
    try:
        # Fetch active alerts
        alerts_snap = (
            monitoring_service.db.collection("doctor_alerts")
            .where("status", "==", "Active")
            .get()
        )
        
        alerts = []
        for doc in alerts_snap:
            data = doc.to_dict()
            # Filter in-memory based on links (to avoid creating composite indexes in Firestore)
            if data.get("patientId") in linked_patients:
                # Format timestamps
                last_taken = data.get("lastTaken")
                if last_taken:
                    last_taken = last_taken.isoformat()
                
                alerts.append({
                    "patientId": data.get("patientId"),
                    "patientName": data.get("patientName"),
                    "missedCount": data.get("missedCount"),
                    "missedMedications": data.get("missedMedications", []),
                    "lastTaken": last_taken,
                    "adherencePercentage": data.get("adherencePercentage"),
                    "updatedAt": data.get("updatedAt").isoformat() if data.get("updatedAt") else None,
                    "status": data.get("status")
                })
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )

@router.post("/run")
def trigger_audit(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["doctor", "caregiver"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
        
    monitoring_service.run_adherence_audit()
    return {"success": True, "detail": "Monitoring audit triggered and completed."}
