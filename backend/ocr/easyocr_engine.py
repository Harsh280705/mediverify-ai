import logging
import easyocr

logger = logging.getLogger(__name__)


class EasyOCREngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._reader = None
        return cls._instance

    def _get_reader(self):
        if self._reader is None:
            self._reader = easyocr.Reader(["en"], gpu=False)
        return self._reader

    def extract_text_lines(self, image):
        """
        Runs EasyOCR on an OpenCV image and returns the detected text lines.
        """

        try:
            reader = self._get_reader()

            results = reader.readtext(image)

            lines = []

            for item in results:
                if len(item) >= 2:
                    text = str(item[1]).strip()

                    if text:
                        lines.append(text)

            return lines

        except Exception as exc:
            logger.exception(exc)
            raise RuntimeError(f"EasyOCR execution failed: {exc}") from exc