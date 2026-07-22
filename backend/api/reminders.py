from fastapi import APIRouter, Depends

from app.dependencies import get_reminder_service

from services.reminder_service import ReminderService

from schemas.reminders import (
    DueReminderResponse,
    ReminderSettingsRequest,
    ReminderSettingsResponse,
)

router = APIRouter(tags=["reminders"])


@router.post("/reminders/settings")
def save_settings(
    payload: ReminderSettingsRequest,
    service: ReminderService = Depends(get_reminder_service),
):

    service.save_settings(payload)

    return {
        "success": True,
    }


@router.get(
    "/reminders/settings",
    response_model=ReminderSettingsResponse,
)
def get_settings(
    patientId: str,
    service: ReminderService = Depends(get_reminder_service),
):

    return service.get_settings(patientId)

@router.get(
    "/reminders/due",
    response_model=DueReminderResponse,
)
def get_due_reminders(
    patientId: str,
    service: ReminderService = Depends(get_reminder_service),
):

    reminders = service.get_due_reminders(patientId)

    return {
        "reminders": reminders
    }

@router.patch(
    "/reminders/{scheduleId}/notification-sent"
)
def mark_notification_sent(
    scheduleId: str,
    service: ReminderService = Depends(get_reminder_service),
):

    service.mark_notification_sent(
        scheduleId
    )

    return {
        "success": True
    }