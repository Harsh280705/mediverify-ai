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
