from firebase.firebase_admin import get_firestore_client


class VerificationService:

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def get_schedule(self, schedule_id: str):

        document = (
            self.db
            .collection("schedules")
            .document(schedule_id)
            .get()
        )

        if not document.exists:
            return None

        data = document.to_dict()

        return {
            "scheduleId": document.id,
            "patientId": data.get("patientId"),
            "medicineName": data.get("medicineName"),
            "strength": data.get("strength"),
            "dosage": data.get("dosage"),
            "instructions": data.get("instructions"),
            "timing": data.get("timing"),
            "scheduledDateTime": data.get("scheduledDateTime"),
            "status": data.get("status"),
        }