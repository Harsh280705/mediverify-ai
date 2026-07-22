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

    def get_user_by_email(self, email: str) -> dict | None:
        snapshots = self.db.collection(USERS_COLLECTION).where("email", "==", email.strip().lower()).limit(1).get()
        if not snapshots:
            return None
        data = snapshots[0].to_dict() or {}
        data['uid'] = snapshots[0].id
        return data

    def link_patient(self, user_uid: str, role: str, patient_uid: str) -> bool:
        doc_ref = self.db.collection(USERS_COLLECTION).document(user_uid)
        field_name = "assignedPatients" if role == "doctor" else "linkedPatients"
        
        from firebase_admin import firestore
        doc_ref.update({
            field_name: firestore.ArrayUnion([patient_uid])
        })
        return True

    def get_linked_patients(self, user_uid: str, role: str) -> list[dict]:
        user_doc = self.get_user(user_uid)
        if not user_doc:
            return []
            
        field_name = "assignedPatients" if role == "doctor" else "linkedPatients"
        patient_ids = user_doc.get(field_name, [])
        if not patient_ids:
            return []
            
        patients = []
        for pid in patient_ids:
            p_doc = self.get_user(pid)
            if p_doc:
                patients.append(p_doc)
        return patients

