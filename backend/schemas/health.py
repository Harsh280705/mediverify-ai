from pydantic import BaseModel


class HealthResponse(BaseModel):
    server: str
    firebase: str
