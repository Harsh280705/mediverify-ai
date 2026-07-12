from datetime import datetime, timezone

from core.constants import USERS_COLLECTION
from firebase.firebase_admin import get_firestore_client


class UserService:
    def __init__(self) -> None:
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def get_user(self, uid: str) -> dict | None:
        snapshot = self.db.collection(USERS_COLLECTION).document(uid).get()
        if not snapshot.exists:
            return None
        data = snapshot.to_dict() or {}
        data['uid'] = snapshot.id
        return data

    def upsert_user(self, uid: str, payload: dict) -> dict:
        record = {
            'name': payload['name'],
            'email': payload['email'],
            'role': payload['role'],
            'created_at': payload.get('created_at') or datetime.now(timezone.utc),
        }
        self.db.collection(USERS_COLLECTION).document(uid).set(record, merge=True)
        return {'uid': uid, **record}
