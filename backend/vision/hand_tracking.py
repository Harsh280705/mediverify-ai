import cv2
import numpy as np
import logging
from vision.yolo_manager import YOLOModelManager

logger = logging.getLogger(__name__)

class HandTracker:
    def __init__(self):
        # MediaPipe Hands references are removed. 
        # YOLO model is lazily loaded via YOLOModelManager.
        pass

    def detect(self, cv_image):
        """
        Detect hand landmarks using YOLO + skin heuristics or fallback.

        Returns:
        {
            "detected": bool,
            "landmarks": list[list[dict]],
            "method": "yolo" | "opencv_fallback" | "error_fallback"
        }
        """
        results = YOLOModelManager.run_inference(cv_image)
        if results is not None:
            try:
                h, w = cv_image.shape[:2]
                landmarks = []
                
                # Look for person detections (class 0)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        if cls_id == 0:  # Person
                            conf = float(box.conf[0])
                            if conf >= 0.4:
                                px1, py1, px2, py2 = box.xyxy[0].tolist()
                                
                                # Crop the body region (exclude head: top 20% of the bounding box)
                                y_start = max(0, int(py1 + (py2 - py1) * 0.2))
                                y_end = min(h, int(py2))
                                x_start = max(0, int(px1))
                                x_max = min(w, int(px2))
                                
                                # Run skin-color check inside body region
                                hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                                lower_skin = np.array([0, 20, 70], dtype=np.uint8)
                                upper_skin = np.array([20, 255, 255], dtype=np.uint8)
                                mask = cv2.inRange(hsv, lower_skin, upper_skin)
                                
                                # Restrict skin detection to the person's body bounding box
                                person_mask = np.zeros_like(mask)
                                person_mask[y_start:y_end, x_start:x_max] = 255
                                mask = cv2.bitwise_and(mask, person_mask)
                                
                                mask = cv2.GaussianBlur(mask, (5, 5), 0)
                                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                                mask = cv2.dilate(mask, kernel, iterations=2)
                                
                                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                
                                for cnt in contours:
                                    area = cv2.contourArea(cnt)
                                    # Medium skin contours represent hands inside person region
                                    if area > 1500:
                                        M = cv2.moments(cnt)
                                        if M["m00"] != 0:
                                            cx = (M["m10"] / M["m00"]) / w
                                            cy = (M["m01"] / M["m00"]) / h
                                        else:
                                            cx = (x_start + (x_max - x_start) / 2) / w
                                            cy = (y_start + (y_end - y_start) / 2) / h
                                            
                                        landmarks.append([
                                            {"x": cx, "y": cy, "z": 0.0},
                                            {"x": cx - 0.05, "y": cy - 0.05, "z": 0.0},
                                            {"x": cx + 0.05, "y": cy - 0.05, "z": 0.0},
                                        ])
                
                if landmarks:
                    return {
                        "detected": True,
                        "landmarks": landmarks,
                        "method": "yolo",
                    }
                    
            except Exception as e:
                logger.exception(f"❌ YOLO hand tracking failed, falling back: {e}")

        # Fall back to OpenCV skin contours heuristic if YOLO or YOLO-based hand detection fails
        return self._opencv_fallback(cv_image)

    def _opencv_fallback(self, cv_image):
        try:
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)

            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)

            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (5, 5),
            )
            mask = cv2.dilate(mask, kernel, iterations=2)

            contours, _ = cv2.findContours(
                mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )

            detected = False
            landmarks = []
            h, w = cv_image.shape[:2]

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 3000:
                    detected = True
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cx = (M["m10"] / M["m00"]) / w
                        cy = (M["m01"] / M["m00"]) / h
                    else:
                        cx = 0.5
                        cy = 0.5

                    landmarks.append(
                        [
                            {"x": cx, "y": cy, "z": 0.0},
                            {"x": cx - 0.05, "y": cy - 0.05, "z": 0.0},
                            {"x": cx + 0.05, "y": cy - 0.05, "z": 0.0},
                        ]
                    )

            return {
                "detected": detected,
                "landmarks": landmarks,
                "method": "opencv_fallback",
            }

        except Exception as e:
            logger.exception(f"❌ OpenCV fallback failed: {e}")
            return {
                "detected": False,
                "landmarks": [],
                "method": "error_fallback",
            }