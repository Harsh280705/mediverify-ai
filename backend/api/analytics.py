from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()

def check_analytics_access(user: dict, patient_id: str):
    role = user.get("role")
    uid = user.get("uid")
    
    if role == "patient":
        if uid != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view your own analytics."
            )
    elif role == "caregiver":
        linked = user.get("linkedPatients", [])
        if patient_id not in linked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Patient is not linked to your caregiver account."
            )
    elif role == "doctor":
        assigned = user.get("assignedPatients", [])
        if patient_id not in assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Patient is not assigned to your doctor account."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid account role."
        )

@router.get("/{patientId}")
def get_patient_analytics(
    patientId: str,
    current_user: dict = Depends(get_current_user)
):
    check_analytics_access(current_user, patientId)
    stats = analytics_service.get_patient_analytics(patientId)
    return stats
