from pathlib import Path

from ocr.loader import ImageLoader
from ocr.preprocess import ImagePreprocessor
from ocr.extractor import OCRExtractor
from ocr.parser import OCRParser


class OCRService:

    def __init__(self):

        self.loader = ImageLoader()
        self.preprocessor = ImagePreprocessor()
        self.extractor = OCRExtractor()

    def extract_text(self, file_path: str):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(path)

        images = self.loader.load(str(path))

        all_lines = []

        for image in images:

            processed = self.preprocessor.preprocess(image)

            lines = self.extractor.extract(processed)

            all_lines.extend(lines)

        return OCRParser.parse_lines(all_lines)