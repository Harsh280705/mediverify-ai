import re
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from firebase.firebase_admin import get_firestore_client

logger = logging.getLogger(__name__)

def parse_duration_to_days(duration_str: str) -> int:
    """
    Parses common duration strings (e.g. '7 days', '1 week', '2 months') into integer number of days.
    """
    if not duration_str:
        return 7  # Default to 7 days if empty
        
    cleaned = duration_str.lower().strip()
    match = re.search(r'(\d+)\s*(day|week|month|year)', cleaned)
    if match:
        val = int(match.group(1))
        unit = match.group(2)
        if 'day' in unit:
            return val
        elif 'week' in unit:
            return val * 7
        elif 'month' in unit:
            return val * 30
        elif 'year' in unit:
            return val * 365
            
    # Check for raw numbers
    match_num = re.search(r'^\d+$', cleaned)
    if match_num:
        return int(match_num.group(0))
        
    return 7  # Fallback

class MedicationService:
    def __init__(self) -> None:
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def confirm_medications(self, patient_id: str, patient_name: str, medications: list[dict]) -> bool:
        """
        Saves confirmed medications to Firestore and generates schedules starting from today.
        """
        try:
            # 1. Save to medical_documents
            doc_ref = self.db.collection("medical_documents").document()
            doc_ref.set({
                "patientId": patient_id,
                "patientName": patient_name,
                "uploadedAt": datetime.now(timezone.utc),
                "medicationsCount": len(medications)
            })

            today = datetime.now(timezone.utc).date()

            # 2. Process each medication
            for med in medications:
                med_ref = self.db.collection("medications").document()
                med_id = med_ref.id
                
                med_doc = {
                    "patientId": patient_id,
                    "medicineName": med["medicineName"],
                    "strength": med.get("strength") or "",
                    "frequency": med.get("frequency") or "",
                    "timings": med.get("timings") or [],
                    "duration": med.get("duration") or "",
                    "instructions": med.get("instructions") or "",
                    "status": "Active",
                    "createdAt": datetime.now(timezone.utc)
                }
                med_ref.set(med_doc)

                # Generate daily schedule documents
                days = parse_duration_to_days(med.get("duration") or "")
                timings = med.get("timings") or []
                
                # Fallback to Morning if no timings are specified
                if not timings:
                    timings = ["Morning"]

                for day_offset in range(days):
                    scheduled_date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                    for timing in timings:
                        sched_ref = self.db.collection("schedules").document()
                        scheduled_datetime = self.get_datetime_for_schedule(
                            scheduled_date,
                            timing
                        )

                        sched_ref.set({
                            "patientId": patient_id,
                            "medicationId": med_id,
                            "medicineName": med["medicineName"],
                            "strength": med.get("strength") or "",

                            "timing": timing,

                            "scheduledDate": scheduled_date,

                            "scheduledDateTime": scheduled_datetime,

                            "status": "Pending",

                            "notificationSentAt":None,
                            
                            "createdAt": datetime.now(timezone.utc)
                        })
            return True
        except Exception as exc:
            logger.error(f"Failed to confirm medications in Firestore: {exc}")
            raise RuntimeError(f"Firestore confirmation write failed: {str(exc)}") from exc

    def get_patient_medications(self, patient_id: str) -> list[dict]:
        """
        Retrieves active medications for a patient, sorted in memory by creation time descending.
        """
        try:
            snapshots = self.db.collection("medications").where("patientId", "==", patient_id).get()
            meds = []
            for snap in snapshots:
                data = snap.to_dict()
                data["id"] = snap.id
                meds.append(data)
            # Sort in memory to avoid indexing issues
            meds.sort(key=lambda x: x.get("createdAt") or datetime.min, reverse=True)
            return meds
        except Exception as exc:
            logger.error(f"Failed to fetch patient medications: {exc}")
            raise RuntimeError(f"Firestore fetch medications failed: {str(exc)}") from exc

    def get_patient_schedule(self, patient_id: str) -> list[dict]:
        """
        Retrieves schedule events for a patient, sorted in memory by date.
        """
        try:
            snapshots = self.db.collection("schedules").where("patientId", "==", patient_id).get()
            scheds = []
            for snap in snapshots:
                data = snap.to_dict()
                data["id"] = snap.id
                scheds.append(data)
            # Sort in memory by scheduledDate ascending, then by timing (for subordering)
            timing_order = {"Morning": 0, "Afternoon": 1, "Evening": 2, "Night": 3}
            scheds.sort(key=lambda x: (x.get("scheduledDate") or "", timing_order.get(x.get("timing"), 99)))
            return scheds
        except Exception as exc:
            logger.error(f"Failed to fetch patient schedule: {exc}")
            raise RuntimeError(f"Firestore fetch schedule failed: {str(exc)}") from exc
        
    def get_time_for_timing(self, timing: str) -> str:

        mapping = {
            "Morning": "08:00",
            "Afternoon": "14:00",
            "Evening": "19:00",
            "Night": "22:00",
        }

        return mapping.get(timing, "08:00")
    
    def get_datetime_for_schedule(
        self,
        scheduled_date: str,
        timing: str
    ) -> datetime:

        time_string = self.get_time_for_timing(timing)

        dt = datetime.strptime(
            f"{scheduled_date} {time_string}",
            "%Y-%m-%d %H:%M"
        )

        return dt.replace(
            tzinfo=ZoneInfo("Asia/Kolkata")
    )
