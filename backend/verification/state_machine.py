import numpy as np
import logging

logger = logging.getLogger(__name__)

class VerificationStateMachine:
    STATES = [
        "WAITING",
        "MEDICINE_FOUND",
        "MATCHED",
        "HAND_PICKED",
        "TABLET_NEAR_MOUTH",
        "TABLET_DISAPPEARED",
        "MOUTH_CLOSED",
        "VERIFYING",
        "TAKEN"
    ]
    
    CONFIDENCE_VALUES = {
        "WAITING": 0,
        "MEDICINE_FOUND": 20,
        "MATCHED": 20,
        "HAND_PICKED": 15,
        "TABLET_NEAR_MOUTH": 15,
        "TABLET_DISAPPEARED": 15,
        "MOUTH_CLOSED": 15
    }

    @classmethod
    def evaluate(cls, detections: dict, current_state: str, history: list) -> tuple:
        """
        Evaluates current tracker detections and determines next state and confidence.
        detections contains:
            "ocr_lines": list[str]
            "yolo_detections": list[dict]
            "hand_detections": dict
            "face_detections": dict
            "match_percentage": float
        
        Returns:
            (new_state: str, updated_history: list, confidence: int)
        """
        history_set = set(history)
        history_set.add("WAITING")

        yolo_classes = [d["class"] for d in detections.get("yolo_detections", [])]
        has_strip_or_box = "medicine_strip" in yolo_classes or "medicine_box" in yolo_classes
        has_ocr = len(detections.get("ocr_lines", [])) > 0
        
        # 1. MEDICINE_FOUND
        if has_strip_or_box or has_ocr:
            history_set.add("MEDICINE_FOUND")
            
        # 2. MATCHED
        match_percentage = detections.get("match_percentage", 0.0)
        if match_percentage >= 70.0:
            history_set.add("MEDICINE_FOUND")
            history_set.add("MATCHED")
            
        # 3. HAND_PICKED
        hand_detected = detections.get("hand_detections", {}).get("detected", False)
        if hand_detected and (has_strip_or_box or "tablet" in yolo_classes or "medicine_strip" in yolo_classes):
            history_set.add("HAND_PICKED")
            
        # 4. TABLET_NEAR_MOUTH
        face_detected = detections.get("face_detections", {}).get("detected", False)
        hand_pts = detections.get("hand_detections", {}).get("landmarks", [])
        
        near_mouth = False
        if hand_detected and face_detected:
            # Check distance between hand center and mouth area
            if hand_pts and len(hand_pts) > 0 and len(hand_pts[0]) > 0:
                h_pt = hand_pts[0][0]  # Get palm center coordinates
                # Assuming mouth is centered around (0.5, 0.65) in the camera field of view
                # Or calculate relative to face detection bounds
                mx, my = 0.5, 0.65
                dist = np.sqrt((h_pt["x"] - mx)**2 + (h_pt["y"] - my)**2)
                if dist < 0.30:  # Hand is near mouth region
                    near_mouth = True
            else:
                # If OpenCV fallback, hand_pts has simulated elements
                if hand_pts:
                    h_pt = hand_pts[0][0]
                    dist = np.sqrt((h_pt["x"] - 0.5)**2 + (h_pt["y"] - 0.65)**2)
                    if dist < 0.30:
                        near_mouth = True
                        
        if near_mouth:
            history_set.add("TABLET_NEAR_MOUTH")
            
        # 5. TABLET_DISAPPEARED
        if "TABLET_NEAR_MOUTH" in history_set:
            # Hand is near mouth, but tablet disappears from scene detection
            if "tablet" not in yolo_classes:
                history_set.add("TABLET_DISAPPEARED")
                
        # 6. MOUTH_CLOSED
        mouth_closed = detections.get("face_detections", {}).get("mouth_closed", True)
        if "TABLET_DISAPPEARED" in history_set and mouth_closed:
            history_set.add("MOUTH_CLOSED")
            
        # Calculate Confidence
        confidence = 0
        for state in cls.CONFIDENCE_VALUES:
            if state in history_set:
                confidence += cls.CONFIDENCE_VALUES[state]
                
        # Determine current state transition based on checklist
        new_state = current_state
        if "MOUTH_CLOSED" in history_set and confidence >= 80:
            new_state = "TAKEN"
        elif "TABLET_DISAPPEARED" in history_set:
            new_state = "TABLET_DISAPPEARED"
        elif "TABLET_NEAR_MOUTH" in history_set:
            new_state = "TABLET_NEAR_MOUTH"
        elif "HAND_PICKED" in history_set:
            new_state = "HAND_PICKED"
        elif "MATCHED" in history_set:
            new_state = "MATCHED"
        elif "MEDICINE_FOUND" in history_set:
            new_state = "MEDICINE_FOUND"
            
        # Sort history to maintain chronological checklist appearance
        updated_history = sorted(
            list(history_set),
            key=lambda x: cls.STATES.index(x) if x in cls.STATES else 99
        )
        
        return new_state, updated_history, confidence
