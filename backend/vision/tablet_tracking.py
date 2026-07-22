import cv2
import numpy as np
import logging
from vision.yolo_manager import YOLOModelManager

logger = logging.getLogger(__name__)

class TabletTracker:
    def __init__(self):
        # YOLO model is lazily loaded and managed via YOLOModelManager.
        pass

    def detect(self, cv_image) -> list:
        """
        Detects tablet, medicine strip, or medicine box.
        Returns:
            list of dicts, each representing a detection:
                {
                    "class": "tablet" | "medicine_strip" | "medicine_box",
                    "confidence": float,
                    "bbox": [x1, y1, x2, y2]
                }
        """
        detections = []
        results = YOLOModelManager.run_inference(cv_image)
        
        if results is not None:
            try:
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        cls_name = r.names[cls_id]
                        conf = float(box.conf[0])
                        xyxy = box.xyxy[0].tolist()
                        
                        # Map general COCO classes if necessary
                        # COCO class 'bottle' can count as medicine container/box, 'cup' as water
                        mapped_class = None
                        if cls_name in ["bottle", "cup", "bowl"]:
                            mapped_class = "medicine_box"
                        
                        if mapped_class:
                            detections.append({
                                "class": mapped_class,
                                "confidence": conf,
                                "bbox": xyxy
                            })
            except Exception as e:
                logger.error(f"YOLO detection parsing failed: {e}")

        # Supplement or fallback with OpenCV contour detection
        opencv_dets = self._opencv_fallback_detect(cv_image)
        # Deduplicate or simply merge
        seen_classes = {d["class"] for d in detections}
        for od in opencv_dets:
            if od["class"] not in seen_classes or od["class"] == "tablet":
                detections.append(od)

        return detections

    def _opencv_fallback_detect(self, cv_image) -> list:
        """
        OpenCV fallback using shapes/contours.
        - Tablets: Small, circular/oval contours.
        - Medicine Strip: Grid-like rectangular contours.
        - Box: Large rectangular shapes.
        """
        detections = []
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)
            
            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                x, y, box_w, box_h = cv2.boundingRect(cnt)
                
                # Check for tablets (small, high circularity)
                if 80 < area < 1200:
                    perimeter = cv2.arcLength(cnt, True)
                    circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                    if circularity > 0.65:
                        detections.append({
                            "class": "tablet",
                            "confidence": round(float(circularity), 2),
                            "bbox": [x, y, x + box_w, y + box_h]
                        })
                
                # Check for medicine strip (medium rectangular contour with aspect ratio ~ 1.5 - 3.0)
                elif 2000 < area < 25000:
                    aspect_ratio = float(box_w) / box_h if box_h > 0 else 0
                    if 0.5 < aspect_ratio < 3.0:
                        detections.append({
                            "class": "medicine_strip",
                            "confidence": 0.70,
                            "bbox": [x, y, x + box_w, y + box_h]
                        })
                
                # Check for box (large, solid rectangle)
                elif area >= 25000:
                    detections.append({
                        "class": "medicine_box",
                        "confidence": 0.75,
                        "bbox": [x, y, x + box_w, y + box_h]
                    })
        except Exception as e:
            logger.error(f"Tablet tracker OpenCV fallback failed: {e}")
            
        return detections
