from ocr.easyocr_engine import EasyOCREngine


class OCRExtractor:

    def __init__(self):

        self.engine = EasyOCREngine()

    def extract(self, image):

        return self.engine.extract_text_lines(image)