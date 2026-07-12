from services.auth_service import AuthService
from services.health_service import HealthService
from services.user_service import UserService


def get_auth_service() -> AuthService:
    return AuthService()


def get_user_service() -> UserService:
    return UserService()


def get_health_service() -> HealthService:
    return HealthService()
