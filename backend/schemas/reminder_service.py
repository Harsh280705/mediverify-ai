from firebase.firebase_admin import get_firestore_client
from core.constants import USERS_COLLECTION


class ReminderService:

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def save_settings(self, payload):

        doc = self.db.collection(USERS_COLLECTION).document(payload.patientId)

        doc.set(
            {
                "notificationsEnabled": payload.notificationsEnabled,
                "browserNotifications": payload.browserNotifications,
                "pushNotifications": payload.pushNotifications,
                "reminderTimes": payload.reminderTimes,
                "remindBeforeMinutes": payload.remindBeforeMinutes,
            },
            merge=True,
        )

    def get_settings(self, patientId: str):

        snapshot = (
            self.db.collection(USERS_COLLECTION)
            .document(patientId)
            .get()
        )

        if not snapshot.exists:
            return None

        data = snapshot.to_dict()

        return {
            "notificationsEnabled": data.get(
                "notificationsEnabled",
                False,
            ),
            "browserNotifications": data.get(
                "browserNotifications",
                False,
            ),
            "pushNotifications": data.get(
                "pushNotifications",
                False,
            ),
            "reminderTimes": data.get(
                "reminderTimes",
                {
                    "Morning": "08:00",
                    "Afternoon": "14:00",
                    "Evening": "19:00",
                    "Night": "22:00",
                },
            ),
            "remindBeforeMinutes": data.get(
                "remindBeforeMinutes",
                15,
            ),
        }