from firebase.firebase_admin import get_firestore_client
from verification.strategy import get_verification_strategy, VerificationStrategy


class VerificationService:

    def __init__(self, strategy: VerificationStrategy = None):
        self._db = None
        self._strategy = strategy if strategy is not None else get_verification_strategy()

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def is_demo_mode(self) -> bool:
        return self._strategy.is_demo_mode()

    def evaluate(self, detections: dict, current_state: str, history: list) -> tuple:
        return self._strategy.evaluate(detections, current_state, history)


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