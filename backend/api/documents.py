import os
import shutil
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.dependencies import (
    get_ocr_service,
    get_prescription_parser,
    get_prescription_service,
)

from ocr.ocr_service import OCRService

from services.prescription_parser import PrescriptionParser
from services.prescription_service import PrescriptionService

from schemas.documents import (
    DocumentUploadResponse,
    DocumentExtractRequest,
    PrescriptionExtractResponse,
    ParsedPrescriptionResponse,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

TEMP_DIR = (
    Path(__file__).resolve().parent.parent
    / "temp"
)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
}


# ============================================================
# Helper Functions
# ============================================================

def validate_upload(file: UploadFile) -> str:
    """
    Validate uploaded file and return its suffix.
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing.",
        )

    suffix = Path(file.filename).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format.",
        )

    return suffix


def save_temp_file(
    file: UploadFile,
    suffix: str,
) -> Path:
    """
    Save uploaded file into the temp directory.
    """

    TEMP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = TEMP_DIR / f"{uuid.uuid4()}{suffix}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return temp_path


def delete_temp_file(path: Path):
    """
    Delete temporary file if it exists.
    """

    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


# ============================================================
# OCR Endpoint
# ============================================================

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    ocr_service: OCRService = Depends(get_ocr_service),
):

    suffix = validate_upload(file)

    temp_path = save_temp_file(
        file,
        suffix,
    )

    try:

        raw_text = ocr_service.extract_text(
            str(temp_path)
        )

        if not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="OCR extracted no text.",
            )

        return DocumentUploadResponse(
            text=raw_text
        )

    finally:

        delete_temp_file(temp_path)


# ============================================================
# LLM Extraction Endpoint
# ============================================================

@router.post(
    "/extract",
    response_model=PrescriptionExtractResponse,
)
async def extract_prescription(
    payload: DocumentExtractRequest,
    prescription_service: PrescriptionService = Depends(
        get_prescription_service
    ),
):

    try:

        extracted = await prescription_service.extract_prescription(
            payload.text
        )

        return PrescriptionExtractResponse(
            **extracted
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM extraction failed: {exc}",
        )


# ============================================================
# Rule-Based Analysis Endpoint
# ============================================================

@router.post(
    "/analyze",
    response_model=ParsedPrescriptionResponse,
)
async def analyze_prescription(
    file: UploadFile = File(...),
    ocr_service: OCRService = Depends(get_ocr_service),
    parser: PrescriptionParser = Depends(
        get_prescription_parser
    ),
):

    suffix = validate_upload(file)

    temp_path = save_temp_file(
        file,
        suffix,
    )

    try:

        raw_text = ocr_service.extract_text(
            str(temp_path)
        )

        if not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="OCR returned empty text.",
            )

        parsed = parser.parse(
            raw_text
        )

        return ParsedPrescriptionResponse(
            **parsed
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    finally:

        delete_temp_file(
            temp_path
        )