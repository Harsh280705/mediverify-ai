from firebase.firebase_admin import is_firebase_connected


class HealthService:
    def get_health_status(self) -> dict[str, str]:
        return {
            'server': 'running',
            'firebase': 'connected' if is_firebase_connected() else 'disconnected',
        }
