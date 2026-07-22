from functools import lru_cache

from services.auth_service import AuthService
from services.health_service import HealthService
from services.user_service import UserService
from services.medication_service import MedicationService
from services.prescription_service import PrescriptionService
from services.prescription_parser import PrescriptionParser
from services.reminder_service import ReminderService

from ocr.ocr_service import OCRService


# ==========================================================
# Core Services
# ==========================================================

@lru_cache
def get_ocr_service() -> OCRService:
    """
    Singleton OCR Service.
    EasyOCR models are loaded only once.
    """
    return OCRService()


@lru_cache
def get_prescription_parser() -> PrescriptionParser:
    """
    Singleton Prescription Parser.
    Loads MedicineMatcher only once.
    """
    return PrescriptionParser()


# ==========================================================
# Business Services
# ==========================================================

@lru_cache
def get_prescription_service() -> PrescriptionService:
    return PrescriptionService()


@lru_cache
def get_medication_service() -> MedicationService:
    return MedicationService()


# ==========================================================
# Existing Services
# ==========================================================

@lru_cache
def get_auth_service() -> AuthService:
    return AuthService()


@lru_cache
def get_user_service() -> UserService:
    return UserService()


@lru_cache
def get_health_service() -> HealthService:
    return HealthService()

@lru_cache
def get_reminder_service():
    return ReminderService()

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
) -> dict:
    token = credentials.credentials
    try:
        claims = auth_service.verify_id_token(token)
        uid = claims.get("uid")
        user = user_service.get_user(uid)
        if not user:
            return {
                "uid": uid,
                "role": claims.get("role", "patient"),
                "name": claims.get("name", "User"),
                "email": claims.get("email", "")
            }
        return user
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired credentials: {exc}"
        )