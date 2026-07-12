from typing import Any

from pydantic import BaseModel, Field


class TokenVerificationRequest(BaseModel):
    id_token: str = Field(min_length=1)


class TokenVerificationResponse(BaseModel):
    valid: bool
    claims: dict[str, Any]
