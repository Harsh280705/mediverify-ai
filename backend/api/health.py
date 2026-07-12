from fastapi import APIRouter, Depends

from app.dependencies import get_health_service
from schemas.health import HealthResponse
from services.health_service import HealthService

router = APIRouter(tags=['health'])


@router.get('/api/health', response_model=HealthResponse)
def health_check(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    return HealthResponse(**service.get_health_status())
