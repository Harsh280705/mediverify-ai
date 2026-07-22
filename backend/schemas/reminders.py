import datetime
from pydantic import BaseModel
from typing import Dict 
from typing import List, Optional


class ReminderSettingsRequest(BaseModel):
    patientId: str
    notificationsEnabled: bool
    browserNotifications: bool
    pushNotifications: bool
    reminderTimes: Dict[str, str]
    remindBeforeMinutes: int


class ReminderSettingsResponse(BaseModel):
    notificationsEnabled: bool
    browserNotifications: bool
    pushNotifications: bool
    reminderTimes: Dict[str, str]
    remindBeforeMinutes: int

class DueReminder(BaseModel):

    id: str

    medicineName: str

    strength: str

    scheduledDateTime: datetime.datetime


class DueReminderResponse(BaseModel):

    reminders: List[DueReminder]


class NotificationSentRequest(BaseModel):

    notificationSentAt: Optional[datetime.datetime] = None