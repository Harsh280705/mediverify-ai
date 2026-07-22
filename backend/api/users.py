from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_user_service
from schemas.user import UserRead, UserUpsert
from services.user_service import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/{uid}', response_model=UserRead)
def read_user(uid: str, service: UserService = Depends(get_user_service)) -> UserRead:
    user = service.get_user(uid)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return UserRead(**user)


@router.post('/{uid}', response_model=UserRead)
def upsert_user(uid: str, payload: UserUpsert, service: UserService = Depends(get_user_service)) -> UserRead:
    user = service.upsert_user(uid, payload.model_dump())
    return UserRead(**user)


from pydantic import BaseModel
from app.dependencies import get_current_user

class LinkPatientRequest(BaseModel):
    patientEmail: str

@router.post('/link-patient')
def link_patient(
    payload: LinkPatientRequest,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    if current_user.get("role") not in ["caregiver", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only caregivers and doctors can link patients"
        )
        
    patient = service.get_user_by_email(payload.patientEmail)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found with the provided email address"
        )
        
    if patient.get("role") != "patient":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user is not a patient"
        )
        
    service.link_patient(current_user["uid"], current_user["role"], patient["uid"])
    return {
        "success": True,
        "patient": {
            "uid": patient["uid"],
            "name": patient["name"],
            "email": patient["email"]
        }
    }

@router.get('/linked-patients')
def get_linked_patients(
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    if current_user.get("role") not in ["caregiver", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only caregivers and doctors can have linked patients"
        )
        
    patients = service.get_linked_patients(current_user["uid"], current_user["role"])
    return [
        {
            "uid": p["uid"],
            "name": p["name"],
            "email": p["email"],
            "role": p["role"]
        } for p in patients
    ]

