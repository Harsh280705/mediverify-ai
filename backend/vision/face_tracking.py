import cv2
import numpy as np
import logging
from vision.yolo_manager import YOLOModelManager

logger = logging.getLogger(__name__)

class FaceMeshTracker:
    def __init__(self):
        # MediaPipe FaceMesh references are removed.
        # YOLO model is lazily loaded via YOLOModelManager.
        self._dark_ratio_history = []
        self._mouth_open_state = False
        self._consecutive_open_count = 0
        self._consecutive_closed_count = 0

    def _update_mouth_state(self, dark_ratio: float) -> tuple:
        if not hasattr(self, "_dark_ratio_history"):
            self._dark_ratio_history = []
        if not hasattr(self, "_mouth_open_state"):
            self._mouth_open_state = False
        if not hasattr(self, "_consecutive_open_count"):
            self._consecutive_open_count = 0
        if not hasattr(self, "_consecutive_closed_count"):
            self._consecutive_closed_count = 0
            
        # Temporal smoothing: maintain history of up to 10 frames
        self._dark_ratio_history.append(dark_ratio)
        if len(self._dark_ratio_history) > 10:
            self._dark_ratio_history.pop(0)
            
        # Confidence averaging
        avg_dark_ratio = sum(self._dark_ratio_history) / len(self._dark_ratio_history)
        
        # Consecutive frame validation / debounce logic:
        # We classify individual frames:
        #   If dark_ratio > 0.36, frame is open
        #   If dark_ratio < 0.30, frame is closed
        if dark_ratio > 0.36:
            self._consecutive_open_count += 1
            self._consecutive_closed_count = 0
        elif dark_ratio < 0.30:
            self._consecutive_closed_count += 1
            self._consecutive_open_count = 0
        else:
            # Decay counts for intermediate values to act as debounce/filter
            self._consecutive_open_count = max(0, self._consecutive_open_count - 1)
            self._consecutive_closed_count = max(0, self._consecutive_closed_count - 1)

        # Hysteresis + Debounce logic:
        # To open: avg_dark_ratio must exceed 0.36 AND we must see at least 3 consecutive open frames
        # To close: avg_dark_ratio must drop below 0.32 AND we must see at least 3 consecutive closed frames
        if self._mouth_open_state:
            if avg_dark_ratio < 0.32 or self._consecutive_closed_count >= 3:
                self._mouth_open_state = False
        else:
            if avg_dark_ratio > 0.36 or self._consecutive_open_count >= 3:
                self._mouth_open_state = True
                
        return self._mouth_open_state, not self._mouth_open_state, avg_dark_ratio

    def _reset_mouth_state(self):
        if hasattr(self, "_dark_ratio_history"):
            self._dark_ratio_history.clear()
        self._mouth_open_state = False
        self._consecutive_open_count = 0
        self._consecutive_closed_count = 0


    def detect(self, cv_image) -> dict:
        """
        Detects facial features (mouth status, head direction) in an OpenCV image.
        Returns:
            dict containing:
                "detected": bool
                "mouth_open": bool
                "mouth_closed": bool
                "head_direction": "center" | "left" | "right"
                "mar": float (mouth aspect ratio / aperture metric)
                "method": "yolo" | "opencv_fallback" | "error_fallback"
        """
        results = YOLOModelManager.run_inference(cv_image)
        if results is not None:
            try:
                h, w = cv_image.shape[:2]
                
                # Look for person detections (class 0)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        if cls_id == 0:  # Person
                            conf = float(box.conf[0])
                            if conf >= 0.4:
                                px1, py1, px2, py2 = box.xyxy[0].tolist()
                                
                                # Crop the head region (top 35% of the person box)
                                face_y1 = max(0, int(py1))
                                face_y2 = min(h, int(py1 + (py2 - py1) * 0.35))
                                face_x1 = max(0, int(px1))
                                face_x2 = min(w, int(px2))
                                
                                # Run skin detection on the frame
                                hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                                lower_skin = np.array([0, 20, 70], dtype=np.uint8)
                                upper_skin = np.array([20, 255, 255], dtype=np.uint8)
                                mask = cv2.inRange(hsv, lower_skin, upper_skin)
                                
                                # Restrict mask to estimated head box
                                face_mask = np.zeros_like(mask)
                                face_mask[face_y1:face_y2, face_x1:face_x2] = 255
                                mask = cv2.bitwise_and(mask, face_mask)
                                
                                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                
                                # Find largest skin contour in face region
                                fx, fy, fw, fh = None, None, None, None
                                max_area = 0
                                for cnt in contours:
                                    area = cv2.contourArea(cnt)
                                    if area > 1000 and area > max_area:
                                        max_area = area
                                        fx, fy, fw, fh = cv2.boundingRect(cnt)
                                
                                # If no skin contour found, use the estimated head box directly
                                if fx is None:
                                    fx, fy, fw, fh = face_x1, face_y1, face_x2 - face_x1, face_y2 - face_y1
                                
                                # If valid box size, compute features
                                if fw > 0 and fh > 0:
                                    # Estimate mouth region: lower 1/3 of the bounding box
                                    mouth_y = int(fy + fh * 0.65)
                                    mouth_h = int(fh * 0.25)
                                    mouth_x = int(fx + fw * 0.25)
                                    mouth_w = int(fw * 0.5)
                                    
                                    # Ensure region is within bounds
                                    mouth_y = max(0, min(mouth_y, h - 1))
                                    mouth_x = max(0, min(mouth_x, w - 1))
                                    mouth_h = max(1, min(mouth_h, h - mouth_y))
                                    mouth_w = max(1, min(mouth_w, w - mouth_x))
                                    
                                    # Calculate dark/light contrast in the mouth region with adaptive thresholding
                                    mouth_roi = cv2.cvtColor(cv_image[mouth_y:mouth_y+mouth_h, mouth_x:mouth_x+mouth_w], cv2.COLOR_BGR2GRAY)
                                    mean_brightness = np.mean(mouth_roi) if mouth_roi.size > 0 else 0.0
                                    adaptive_thresh = int(np.clip(mean_brightness * 0.55, 20, 85))
                                    _, thresholded = cv2.threshold(mouth_roi, adaptive_thresh, 255, cv2.THRESH_BINARY_INV)
                                    dark_pixels = cv2.countNonZero(thresholded)
                                    total_pixels = mouth_roi.size
                                    
                                    dark_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0.0
                                    mouth_open, mouth_closed, smoothed_mar = self._update_mouth_state(dark_ratio)
                                    
                                    # Estimate head direction from face center relative to image center
                                    box_center_x = fx + fw / 2
                                    img_center_x = w / 2
                                    offset = (box_center_x - img_center_x) / img_center_x
                                    
                                    direction = "center"
                                    if offset < -0.15:
                                        direction = "right"
                                    elif offset > 0.15:
                                        direction = "left"
                                        
                                    return {
                                        "detected": True,
                                        "mouth_open": mouth_open,
                                        "mouth_closed": mouth_closed,
                                        "head_direction": direction,
                                        "mar": smoothed_mar,
                                        "method": "yolo"
                                    }
            except Exception as e:
                logger.error(f"YOLO Face tracking processing failed: {e}")

        # Fallback to OpenCV contour heuristic
        return self._opencv_fallback(cv_image)

    def _opencv_fallback(self, cv_image) -> dict:
        """
        OpenCV fallback face-like region and mouth area color heuristic.
        """
        try:
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            h, w = cv_image.shape[:2]
            
            detected = False
            mouth_open = False
            direction = "center"
            mar = 0.0
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 10000:  # Large skin-colored region (likely a face)
                    x, y, box_w, box_h = cv2.boundingRect(cnt)
                    detected = True
                    
                    # Estimate mouth region: lower 1/3 of the bounding box
                    mouth_y = int(y + box_h * 0.65)
                    mouth_h = int(box_h * 0.25)
                    mouth_x = int(x + box_w * 0.25)
                    mouth_w = int(box_w * 0.5)
                    
                    # Ensure region is within bounds
                    mouth_y = max(0, min(mouth_y, h - 1))
                    mouth_x = max(0, min(mouth_x, w - 1))
                    mouth_h = max(1, min(mouth_h, h - mouth_y))
                    mouth_w = max(1, min(mouth_w, w - mouth_x))
                    
                    mouth_roi = cv2.cvtColor(cv_image[mouth_y:mouth_y+mouth_h, mouth_x:mouth_x+mouth_w], cv2.COLOR_BGR2GRAY)
                    
                    # Calculate dark/light contrast in the mouth region with adaptive thresholding (mouth opening shows a dark cavity)
                    mean_brightness = np.mean(mouth_roi) if mouth_roi.size > 0 else 0.0
                    adaptive_thresh = int(np.clip(mean_brightness * 0.55, 20, 85))
                    _, thresholded = cv2.threshold(mouth_roi, adaptive_thresh, 255, cv2.THRESH_BINARY_INV)
                    dark_pixels = cv2.countNonZero(thresholded)
                    total_pixels = mouth_roi.size
                    
                    dark_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0
                    mouth_open, mouth_closed, smoothed_mar = self._update_mouth_state(dark_ratio)
                    
                    # Estimate head direction from box center relative to image center
                    box_center_x = x + box_w / 2
                    img_center_x = w / 2
                    offset = (box_center_x - img_center_x) / img_center_x
                    
                    if offset < -0.15:
                        direction = "right"
                    elif offset > 0.15:
                        direction = "left"
                    break
            
            if not detected:
                self._reset_mouth_state()
                mouth_open = False
                mouth_closed = True
                smoothed_mar = 0.0
            
            return {
                "detected": detected,
                "mouth_open": mouth_open,
                "mouth_closed": mouth_closed,
                "head_direction": direction,
                "mar": smoothed_mar,
                "method": "opencv_fallback"
            }
        except Exception as e:
            logger.error(f"Face tracker OpenCV fallback failed: {e}")
            self._reset_mouth_state()
            return {
                "detected": False,
                "mouth_open": False,
                "mouth_closed": True,
                "head_direction": "center",
                "mar": 0.0,
                "method": "error_fallback"
            }

# Interface preservation alias
FaceTracker = FaceMeshTracker
