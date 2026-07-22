from pathlib import Path

import cv2
import numpy as np

from PIL import Image

from pdf2image import convert_from_path

import pillow_heif


class ImageLoader:

    SUPPORTED_IMAGE_FORMATS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
        ".heic",
    }

    SUPPORTED_DOCUMENT_FORMATS = {
        ".pdf"
    }

    @staticmethod
    def load(file_path: str):

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        extension = file_path.suffix.lower()

        if extension in ImageLoader.SUPPORTED_IMAGE_FORMATS:
            return ImageLoader._load_image(file_path)

        elif extension in ImageLoader.SUPPORTED_DOCUMENT_FORMATS:
            return ImageLoader._load_pdf(file_path)

        raise ValueError(
            f"Unsupported file type : {extension}"
        )

    @staticmethod
    def _load_image(path: Path):

        if path.suffix.lower() == ".heic":

            return ImageLoader._load_heic(path)

        image = cv2.imread(str(path))

        if image is None:
            raise ValueError("Unable to read image.")

        return [image]

    @staticmethod
    def _load_heic(path: Path):

        heif = pillow_heif.read_heif(str(path))

        image = Image.frombytes(
            heif.mode,
            heif.size,
            heif.data,
            "raw"
        )

        image = cv2.cvtColor(
            np.array(image),
            cv2.COLOR_RGB2BGR
        )

        return [image]

    @staticmethod
    def _load_pdf(path: Path):

        pages = convert_from_path(
            str(path),
            dpi=300
        )

        images = []

        for page in pages:

            page = cv2.cvtColor(
                np.array(page),
                cv2.COLOR_RGB2BGR
            )

            images.append(page)

        return images
    
    