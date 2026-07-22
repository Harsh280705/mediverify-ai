from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class MedicationConfirmItem(BaseModel):
    medicineName: str = Field(min_length=1)
    strength: str = Field(default="")
    frequency: str = Field(default="")
    timings: List[str] = Field(default_factory=list)
    duration: str = Field(default="")
    instructions: str = Field(default="")

class MedicationConfirmRequest(BaseModel):
    patientId: str = Field(min_length=1)
    patientName: str = Field(default="")
    medications: List[MedicationConfirmItem]

class MedicationResponseItem(MedicationConfirmItem):
    id: str
    patientId: str
    status: str
    createdAt: datetime

class ScheduleResponseItem(BaseModel):
    id: str
    patientId: str
    medicationId: str
    medicineName: str
    strength: str
    timing: str
    scheduledDate: str
    status: str
