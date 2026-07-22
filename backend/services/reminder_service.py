from firebase.firebase_admin import get_firestore_client
from core.constants import USERS_COLLECTION
from datetime import datetime, timezone, timedelta


class ReminderService:

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def save_settings(self, payload):

        self.db.collection(USERS_COLLECTION).document(
            payload.patientId
        ).set(
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
            return {
                "notificationsEnabled": False,
                "browserNotifications": False,
                "pushNotifications": False,
                "reminderTimes": {
                    "Morning": "08:00",
                    "Afternoon": "14:00",
                    "Evening": "19:00",
                    "Night": "22:00",
                },
                "remindBeforeMinutes": 15,
            }

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
    
    def get_due_reminders(self, patientId: str):

        user = (
            self.db.collection(USERS_COLLECTION)
            .document(patientId)
            .get()
        )

        remind_before = 15

        if user.exists:

            remind_before = (
                user.to_dict().get(
                    "remindBeforeMinutes",
                    15,
                )
            )

        snapshots = (
            self.db.collection("schedules")
            .where("patientId", "==", patientId)
            .where("status", "==", "Pending")
            .get()
        )

        now = datetime.now(timezone.utc)

        reminders = []

        for snap in snapshots:

            data = snap.to_dict()

            scheduled = data.get(
                "scheduledDateTime"
            )

            if scheduled is None:
                continue

            if data.get(
                "notificationSentAt"
            ):
                continue

            reminder_time = (
                scheduled -
                timedelta(
                    minutes=remind_before
                )
            )
        

            if now >= reminder_time:

                reminders.append({

                    "id": snap.id,

                    "medicineName":
                    data.get("medicineName"),

                    "strength":
                    data.get("strength"),

                    "scheduledDateTime":
                    scheduled,

                })

        return reminders
    
    def mark_notification_sent(
        self,
        scheduleId: str,
    ):

        self.db.collection(
            "schedules"
        ).document(
            scheduleId
        ).update({

            "notificationSentAt":
            datetime.now(timezone.utc)

        })