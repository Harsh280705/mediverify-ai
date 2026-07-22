from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.dependencies import get_medication_service
from services.medication_service import MedicationService
from schemas.medications import (
    MedicationConfirmRequest,
    MedicationResponseItem,
    ScheduleResponseItem
)

router = APIRouter(tags=['medications'])

@router.post('/medications/confirm', status_code=status.HTTP_201_CREATED)
def confirm_medications(
    payload: MedicationConfirmRequest,
    service: MedicationService = Depends(get_medication_service)
) -> dict:
    try:
        meds_dict = [m.model_dump() for m in payload.medications]
        service.confirm_medications(payload.patientId, payload.patientName, meds_dict)
        return {"success": True, "detail": "Medications saved and schedule generated successfully."}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm medications: {str(exc)}"
        )

@router.get('/medications', response_model=List[MedicationResponseItem])
def get_medications(
    patientId: str,
    service: MedicationService = Depends(get_medication_service)
) -> List[MedicationResponseItem]:
    try:
        meds = service.get_patient_medications(patientId)
        return meds
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve medications: {str(exc)}"
        )

@router.get('/schedule', response_model=List[ScheduleResponseItem])
def get_schedule(
    patientId: str,
    service: MedicationService = Depends(get_medication_service)
) -> List[ScheduleResponseItem]:
    try:
        schedule = service.get_patient_schedule(patientId)
        return schedule
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schedule: {str(exc)}"
        )
