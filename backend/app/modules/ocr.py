"""Module 3: OCR Preprocessing, Text Extraction, and Field Parser."""

import re
import datetime
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np


class DocumentOCREngine:
    def __init__(self):
        self.version = "ocr-baseline-v1"

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """OpenCV preprocessing pipeline: grayscale, denoise, and adaptive thresholding."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Denoise using bilateral filter (preserves edges of letters)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # Contrast enhancement via CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        return enhanced

    def extract_text_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect potential text line bounding boxes using morphological gradients."""
        preprocessed = self.preprocess(image)
        h, w = preprocessed.shape[:2]

        # Morphological gradient to highlight text edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        grad = cv2.morphologyEx(preprocessed, cv2.MORPH_GRADIENT, kernel)
        _, thresh = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Connect text characters into horizontal lines
        connected_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
        connected = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, connected_kernel)

        contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions = []
        for c in contours:
            x, y, rw, rh = cv2.boundingRect(c)
            # Filter non-text proportions
            if rw > 40 and 10 < rh < 120 and (rw / rh) > 1.5:
                regions.append({
                    "bbox": [int(x), int(y), int(rw), int(rh)],
                    "confidence": 0.92,
                })

        # Sort top-to-bottom
        regions.sort(key=lambda r: r["bbox"][1])
        return regions

    def parse_fields_from_text(self, raw_text: str) -> Dict[str, Dict[str, Any]]:
        """Parse structured identity fields from OCR text using deterministic regex patterns."""
        fields: Dict[str, Dict[str, Any]] = {}
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # 1. Document Number Pattern (Handle multi-word labels and optional hyphens)
        doc_labeled = re.search(r"(?:DOCUMENT\s+NUMBER|PASSPORT\s+NUMBER|PASSPORT\s+NO|DOCUMENT\s+NO|DOCUMENT|PASSPORT|NUMBER|NO)[:\s]+([A-Z0-9-]{6,16})\b", raw_text, re.IGNORECASE)
        if doc_labeled:
            val = doc_labeled.group(1).upper()
            if any(c.isdigit() for c in val):
                fields["document_number"] = {
                    "value": val,
                    "confidence": 0.95,
                    "source": "OCR",
                }

        if "document_number" not in fields:
            doc_match = re.search(r"\b([A-Z]{1,2}[0-9]{6,8}|[0-9]{8,10})\b", raw_text)
            if doc_match:
                fields["document_number"] = {
                    "value": doc_match.group(1).upper(),
                    "confidence": 0.90,
                    "source": "OCR",
                }

        # 2. Date of Birth Pattern (Support DATE OF BIRTH, BIRTH DATE, DOB)
        dob_match = re.search(r"(?:DATE\s+OF\s+BIRTH|BIRTH\s+DATE|DOB|BIRTH)[:\s]+([0-9]{2}[-/.][0-9]{2}[-/.][0-9]{4}|[0-9]{4}[-/.][0-9]{2}[-/.][0-9]{2})", raw_text, re.IGNORECASE)
        if dob_match:
            fields["date_of_birth"] = {
                "value": self._standardize_date(dob_match.group(1)),
                "confidence": 0.90,
                "source": "OCR",
            }

        # 3. Expiry Date Pattern (Support EXPIRY DATE, DATE OF EXPIRY, EXPIRATION DATE)
        exp_match = re.search(r"(?:EXPIRY\s+DATE|DATE\s+OF\s+EXPIRY|EXPIRATION\s+DATE|EXPIRY|EXPIRATION)[:\s]+([0-9]{2}[-/.][0-9]{2}[-/.][0-9]{4}|[0-9]{4}[-/.][0-9]{2}[-/.][0-9]{2})", raw_text, re.IGNORECASE)
        if exp_match:
            fields["expiry_date"] = {
                "value": self._standardize_date(exp_match.group(1)),
                "confidence": 0.90,
                "source": "OCR",
            }

        # 4. Nationality / Country Code (3-letter ISO 3166-1 alpha-3 code)
        nat_match = re.search(r"(?:NAT|NATIONALITY|CODE)[:\s]*([A-Z]{3})\b", raw_text, re.IGNORECASE)
        if nat_match:
            fields["nationality"] = {
                "value": nat_match.group(1).upper(),
                "confidence": 0.92,
                "source": "OCR",
            }

        # 5. Name extraction (Surname / Given names)
        name_match = re.search(r"(?:NAME|SURNAME|NOM)[:\s]*([A-Z\s,]+)", raw_text, re.IGNORECASE)
        if name_match:
            clean_name = name_match.group(1).strip().replace(",", " ")
            clean_name = " ".join(clean_name.split()[:4])
            if clean_name:
                fields["name"] = {
                    "value": clean_name,
                    "confidence": 0.88,
                    "source": "OCR",
                }

        return fields

    def _standardize_date(self, date_str: str) -> str:
        """Convert varied date formats to ISO YYYY-MM-DD format."""
        clean = date_str.replace("/", "-").replace(".", "-")
        parts = clean.split("-")
        if len(parts) == 3:
            if len(parts[0]) == 4:  # YYYY-MM-DD
                return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
            elif len(parts[2]) == 4:  # DD-MM-YYYY
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        return date_str


ocr_engine = DocumentOCREngine()
