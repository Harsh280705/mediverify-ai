from typing import List, Optional
from pydantic import BaseModel, Field

# ============================================================================
# OCR RESPONSE
# ============================================================================

class DocumentUploadResponse(BaseModel):
    text: str


class DocumentExtractRequest(BaseModel):
    text: str


# ============================================================================
# LLM EXTRACTION RESPONSE
# (Existing endpoint: /documents/extract)
# ============================================================================

class MedicationExtractItem(BaseModel):
    medicineName: str = ""
    strength: str = ""
    frequency: str = ""
    timings: List[str] = Field(default_factory=list)
    duration: str = ""
    instructions: str = ""


class PrescriptionExtractResponse(BaseModel):
    patientName: str = ""
    medications: List[MedicationExtractItem] = Field(default_factory=list)


# ============================================================================
# RULE-BASED PARSER RESPONSE
# (New endpoint: /documents/analyze)
# ============================================================================

class MedicineMatch(BaseModel):
    generic: str = ""
    brand: str = ""
    confidence: float = 0.0


class MedicineSchedule(BaseModel):
    morning: bool = False
    afternoon: bool = False
    evening: bool = False
    night: bool = False


class ParsedMedicine(BaseModel):

    ocr_name: str

    matched: List[MedicineMatch] = Field(default_factory=list)

    type: Optional[str] = None

    strength: Optional[str] = None

    schedule: MedicineSchedule

    meal: Optional[str] = None

    duration_days: Optional[int] = None


class ParsedPrescriptionResponse(BaseModel):

    doctor: Optional[str] = None

    hospital: Optional[str] = None

    patient_name: Optional[str] = None

    age: Optional[int] = None

    gender: Optional[str] = None

    date: Optional[str] = None

    diagnosis: Optional[str] = None

    follow_up: Optional[str] = None

    advice: List[str] = Field(default_factory=list)

    medicines: List[ParsedMedicine] = Field(default_factory=list)