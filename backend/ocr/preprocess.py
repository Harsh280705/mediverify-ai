import cv2
import numpy as np


class ImagePreprocessor:
    """
    Handles preprocessing before OCR.
    Input  : OpenCV image (BGR)
    Output : OpenCV image (BGR)
    """

    @staticmethod
    def preprocess(image: np.ndarray) -> np.ndarray:

        # Keep a copy
        processed = image.copy()

        # Upscale small images
        height, width = processed.shape[:2]

        if max(height, width) < 1200:
            processed = cv2.resize(
                processed,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_CUBIC,
            )

        # Reduce noise while preserving edges
        processed = cv2.bilateralFilter(
            processed,
            d=9,
            sigmaColor=75,
            sigmaSpace=75,
        )

        # Increase contrast using LAB color space
        lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)

        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        l = clahe.apply(l)

        lab = cv2.merge((l, a, b))

        processed = cv2.cvtColor(
            lab,
            cv2.COLOR_LAB2BGR,
        )

        return processed