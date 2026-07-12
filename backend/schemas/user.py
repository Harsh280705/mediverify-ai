from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserUpsert(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    role: str = Field(pattern='^(patient|caregiver)$')


class UserRead(UserUpsert):
    uid: str
    created_at: datetime | None = None
