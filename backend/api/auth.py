from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_auth_service
from schemas.auth import TokenVerificationRequest, TokenVerificationResponse
from services.auth_service import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/verify-token', response_model=TokenVerificationResponse)
def verify_token(
    payload: TokenVerificationRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenVerificationResponse:
    try:
        claims = service.verify_id_token(payload.id_token)
        return TokenVerificationResponse(valid=True, claims=claims)
    except Exception as exc:  # pragma: no cover - defensive wrapper for external SDK errors
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication token') from exc
