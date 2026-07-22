import logging
import threading
import time
import asyncio
from datetime import datetime, timezone, timedelta
from firebase.firebase_admin import get_firestore_client
from core.constants import USERS_COLLECTION

logger = logging.getLogger(__name__)

class DoctorMonitoringService:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def run_adherence_audit(self):
        """
        Scans all patients, checks for missed medications (Pending > 2 hours past due),
        calculates adherence rates, and manages doctor alerts.
        """
        logger.info("Starting doctor monitoring adherence audit...")
        try:
            # 1. Fetch all patient users
            patients_snap = self.db.collection(USERS_COLLECTION).where("role", "==", "patient").get()
            
            now = datetime.now(timezone.utc)
            grace_period = timedelta(hours=2)
            
            for p_doc in patients_snap:
                patient_id = p_doc.id
                patient_data = p_doc.to_dict()
                patient_name = patient_data.get("name", "Unknown Patient")
                
                # Fetch all schedules for this patient
                schedules_snap = self.db.collection("schedules").where("patientId", "==", patient_id).get()
                
                schedules = []
                for s in schedules_snap:
                    data = s.to_dict()
                    data["id"] = s.id
                    schedules.append(data)
                
                if not schedules:
                    continue
                
                # Group schedules into Taken, Pending, and Missed (due > 2 hours ago)
                taken_count = 0
                missed_count = 0
                last_taken = None
                missed_meds = []
                
                for sched in schedules:
                    status = sched.get("status", "Pending")
                    scheduled_dt = sched.get("scheduledDateTime")
                    
                    if not scheduled_dt:
                        continue
                        
                    # Handle TZ aware vs naive
                    if scheduled_dt.tzinfo is None:
                        scheduled_dt = scheduled_dt.replace(tzinfo=timezone.utc)
                        
                    if status == "Taken":
                        taken_count += 1
                        taken_at = sched.get("takenAt")
                        if taken_at:
                            if taken_at.tzinfo is None:
                                taken_at = taken_at.replace(tzinfo=timezone.utc)
                            if last_taken is None or taken_at > last_taken:
                                last_taken = taken_at
                    elif status == "Pending":
                        if now > (scheduled_dt + grace_period):
                            # It is missed!
                            missed_count += 1
                            missed_meds.append(sched.get("medicineName", "Medication"))
                
                # Calculate adherence percentage for past scheduled items
                total_past_doses = taken_count + missed_count
                adherence_pct = 100.0
                if total_past_doses > 0:
                    adherence_pct = round((taken_count / total_past_doses) * 100, 2)
                    
                # 2. Manage alerts in doctor_alerts collection
                alert_ref = self.db.collection("doctor_alerts").document(patient_id)
                
                if missed_count >= 2:
                    alert_doc = {
                        "patientId": patient_id,
                        "patientName": patient_name,
                        "missedCount": missed_count,
                        "missedMedications": list(set(missed_meds)),
                        "lastTaken": last_taken,
                        "adherencePercentage": adherence_pct,
                        "updatedAt": now,
                        "status": "Active"
                    }
                    alert_ref.set(alert_doc, merge=True)
                    logger.info(f"Alert raised/updated for patient {patient_name} (Missed: {missed_count})")
                else:
                    # If an alert exists, resolve it or mark it inactive
                    alert_doc = alert_ref.get()
                    if alert_doc.exists and alert_doc.to_dict().get("status") == "Active":
                        alert_ref.update({
                            "status": "Resolved",
                            "resolvedAt": now,
                            "missedCount": missed_count,
                            "adherencePercentage": adherence_pct
                        })
                        logger.info(f"Alert resolved for patient {patient_name}")
                        
            logger.info("Adherence audit completed successfully.")
        except Exception as e:
            logger.error(f"Adherence audit failed: {e}")

# Helper to start the background thread inside FastAPI app startup
def start_doctor_monitoring_daemon():
    def daemon_loop():
        service = DoctorMonitoringService()
        while True:
            try:
                service.run_adherence_audit()
            except Exception as e:
                logger.error(f"Error in daemon audit: {e}")
            # Run check every 30 minutes
            time.sleep(1800)

    t = threading.Thread(target=daemon_loop, daemon=True)
    t.start()
    logger.info("Doctor monitoring daemon started.")
