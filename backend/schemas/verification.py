from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any

class VerificationResponse(BaseModel):
    scheduleId: str
    patientId: str
    medicineName: str
    strength: str | None = None
    dosage: str | None = None
    instructions: str | None = None
    timing: str | None = None
    scheduledDateTime: datetime
    status: str

class ProcessFrameRequest(BaseModel):
    frame: str
    currentState: str
    history: List[str]
    confidence: int

class ProcessFrameResponse(BaseModel):
    currentState: str
    history: List[str]
    confidence: int
    summary: str
    ocrLines: List[str]
    matchPercentage: float
    yoloDetections: List[Dict[str, Any]]
    handDetections: Dict[str, Any]
    faceDetections: Dict[str, Any]
    statusUpdated: bool = False