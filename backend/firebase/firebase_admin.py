from __future__ import annotations

from pathlib import Path

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials, firestore, storage

from config.settings import get_settings

_firebase_app = None


def initialize_firebase_admin():
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    settings = get_settings()
    options: dict[str, str] = {}

    if settings.project_id:
        options['projectId'] = settings.project_id

    if settings.service_account_path:
        credential_path = Path(settings.service_account_path)
        if not credential_path.exists():
            raise FileNotFoundError(f'Service account file not found: {credential_path}')
        cred = credentials.Certificate(str(credential_path))
        _firebase_app = firebase_admin.initialize_app(cred, options or None)
    else:
        _firebase_app = firebase_admin.initialize_app(options=options or None)

    return _firebase_app


def _ensure_app():
    return _firebase_app or initialize_firebase_admin()


def get_firestore_client():
    return firestore.client(app=_ensure_app())


def get_auth_client():
    return firebase_auth


def get_storage_bucket():
    return storage.bucket(app=_ensure_app())


def is_firebase_connected() -> bool:
    try:
        _ensure_app()
        get_firestore_client()
        return True
    except Exception:
        return False
