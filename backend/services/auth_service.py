from firebase.firebase_admin import get_auth_client


class AuthService:
    def __init__(self) -> None:
        self._auth = get_auth_client()

    def verify_id_token(self, id_token: str) -> dict:
        return self._auth.verify_id_token(id_token)
