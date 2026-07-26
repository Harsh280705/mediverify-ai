from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import base64
import cv2
import numpy as np
from datetime import datetime, timezone

from schemas.verification import VerificationResponse, ProcessFrameRequest, ProcessFrameResponse
from services.verification_service import VerificationService
from services.summary_service import SummaryService
from services.medicine_matcher import MedicineMatcher
from app.dependencies import get_current_user

from verification.state_machine import VerificationStateMachine
from vision.hand_tracking import HandTracker
from vision.tablet_tracking import TabletTracker
from vision.face_tracking import FaceMeshTracker
from ocr.easyocr_engine import EasyOCREngine
from rapidfuzz import fuzz

router = APIRouter(tags=["verification"])

# Instantiate trackers and engines once (lazy loading/singletons)
easyocr_engine = EasyOCREngine()
hand_tracker = HandTracker()
tablet_tracker = TabletTracker()
face_tracker = FaceMeshTracker()
summary_service = SummaryService()
medicine_matcher = MedicineMatcher()

def get_verification_service():
    return VerificationService()

def check_schedule_access(user: dict, schedule: dict):
    """
    Enforces that patients own their schedules, and caregivers/doctors can only access linked/assigned patients.
    """
    role = user.get("role")
    uid = user.get("uid")
    patient_id = schedule.get("patientId")
    
    if role == "patient":
        if uid != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not own this schedule."
            )
    elif role == "caregiver":
        linked = user.get("linkedPatients", [])
        if patient_id not in linked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. This patient is not linked to your caregiver account."
            )
    elif role == "doctor":
        assigned = user.get("assignedPatients", [])
        if patient_id not in assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. This patient is not assigned to your doctor account."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid account role."
        )

@router.get(
    "/verification/{scheduleId}",
    response_model=VerificationResponse,
)
def get_verification(
    scheduleId: str,
    service: VerificationService = Depends(get_verification_service),
    current_user: dict = Depends(get_current_user),
):
    schedule = service.get_schedule(scheduleId)
    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    check_schedule_access(current_user, schedule)
    schedule["demoMode"] = service.is_demo_mode()
    return schedule

@router.post(
    "/verification/{scheduleId}/process-frame",
    response_model=ProcessFrameResponse,
)
async def process_frame(
    scheduleId: str,
    payload: ProcessFrameRequest,
    service: VerificationService = Depends(get_verification_service),
    current_user: dict = Depends(get_current_user),
):
    # 1. Fetch schedule and check access
    schedule = service.get_schedule(scheduleId)
    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    check_schedule_access(current_user, schedule)

    # 2. Decode the base64 image frame
    try:
        frame_data = payload.frame
        if "," in frame_data:
            header, encoded = frame_data.split(",", 1)
        else:
            encoded = frame_data
        
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("CV2 failed to decode frame image")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 frame data: {str(e)}"
        )

    # 3. Perform detections
    # OCR (EasyOCR)
    ocr_lines = []
    try:
        ocr_lines = easyocr_engine.extract_text_lines(img)
    except Exception as e:
        # Keep process running even if OCR errors out temporarily
        ocr_lines = []

    # Calculate robust medicine match confidence using multi-stage matching
    expected_med = schedule.get("medicineName", "")
    expected_strength = schedule.get("strength", "")
    expected_dosage = schedule.get("dosage", "")
    
    best_match_score = medicine_matcher.calculate_match_confidence(
        ocr_lines=ocr_lines,
        expected_name=expected_med,
        expected_strength=expected_strength,
        expected_dosage=expected_dosage
    )
            
    # YOLO Tracker
    yolo_dets = tablet_tracker.detect(img)
    
    # Hand Tracker
    hand_dets = hand_tracker.detect(img)
    
    # Face Mesh Tracker
    face_dets = face_tracker.detect(img)

    # 4. State Machine Evaluation
    detections = {
        "ocr_lines": ocr_lines,
        "yolo_detections": yolo_dets,
        "hand_detections": hand_dets,
        "face_detections": face_dets,
        "match_percentage": best_match_score
    }

    new_state, updated_history, new_confidence = service.evaluate(
        detections,
        payload.currentState,
        payload.history
    )

    # 5. Fetch Ollama medication summary if matched
    summary = ""
    if "MATCHED" in updated_history or best_match_score >= 70.0:
        try:
            summary = await summary_service.get_or_generate_summary(
                medicine_name=schedule.get("medicineName"),
                strength=schedule.get("strength", ""),
                dosage=schedule.get("dosage", ""),
                instructions=schedule.get("instructions", ""),
                timing=schedule.get("timing", "")
            )
        except Exception as e:
            summary = f"Expected medicine matched: {expected_med}."

    # 6. Update Firestore once if confidence threshold met
    status_updated = False
    if (new_state == "TAKEN" or new_confidence >= 80) and schedule.get("status") != "Taken":
        try:
            # Update Firestore schedule state
            service.db.collection("schedules").document(scheduleId).update({
                "status": "Taken",
                "takenAt": datetime.now(timezone.utc),
                "verificationConfidence": new_confidence,
                "verificationMethod": "AI_VISION"
            })
            status_updated = True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update verification status in database: {e}"
            )

    return ProcessFrameResponse(
        currentState=new_state,
        history=updated_history,
        confidence=new_confidence,
        summary=summary,
        ocrLines=ocr_lines,
        matchPercentage=best_match_score,
        yoloDetections=yolo_dets,
        handDetections=hand_dets,
        faceDetections=face_dets,
        statusUpdated=status_updated,
        demoMode=service.is_demo_mode()
    )