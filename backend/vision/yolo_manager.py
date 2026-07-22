import logging
import cv2

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
    logger.warning("Ultralytics YOLO is not installed in the environment.")

class YOLOModelManager:
    _model = None
    _last_image_id = None
    _last_results = None

    @classmethod
    def get_model(cls):
        """
        Lazy loads the YOLO model once and returns it.
        """
        if YOLO is None:
            return None
            
        if cls._model is None:
            try:
                # Use yolov8n.pt which is already in the backend folder
                cls._model = YOLO("yolov8n.pt")
                logger.info("✅ YOLO model yolov8n.pt initialized successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to load YOLO model: {e}")
                cls._model = None
        return cls._model

    @classmethod
    def run_inference(cls, cv_image):
        """
        Runs YOLO inference on the image, caching the results for the current frame.
        """
        model = cls.get_model()
        if model is None:
            return None

        # Build a cache key using the object identity, shape, and base array info.
        # This is fast and safe within the scope of a single API request process.
        image_id = (id(cv_image), cv_image.shape, getattr(cv_image, 'base', None))
        
        if cls._last_image_id == image_id and cls._last_results is not None:
            logger.debug("🎯 YOLO inference cache hit!")
            return cls._last_results

        try:
            results = model(cv_image, verbose=False)
            cls._last_image_id = image_id
            cls._last_results = results
            return results
        except Exception as e:
            logger.error(f"❌ YOLO inference failed: {e}")
            return None
