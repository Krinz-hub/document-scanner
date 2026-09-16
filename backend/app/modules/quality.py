"""Module 1: Document Image Quality Assessment."""

from typing import Dict, Any, List
import cv2
import numpy as np


class ImageQualityAssessor:
    def __init__(
        self,
        blur_threshold: float = 100.0,
        glare_threshold_ratio: float = 0.03,
        min_width: int = 600,
        min_height: int = 400,
    ):
        self.blur_threshold = blur_threshold
        self.glare_threshold_ratio = glare_threshold_ratio
        self.min_width = min_width
        self.min_height = min_height

    def assess_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """Assess quality from raw image bytes."""
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return {
                "status": "LOW_IMAGE_QUALITY",
                "score": 0.0,
                "issues": ["Corrupted or unreadable image file"],
                "metrics": {},
            }
        return self.assess(img)

    def assess(self, image: np.ndarray) -> Dict[str, Any]:
        """Assess quality from an OpenCV BGR image."""
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        issues: List[str] = []

        # 1. Blur Assessment via Laplacian Variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())
        is_blurry = blur_score < self.blur_threshold
        if is_blurry:
            issues.append(f"Blur detected (variance score {blur_score:.1f} below threshold {self.blur_threshold:.1f})")

        # 2. Glare Assessment via high-luminance pixel ratio (truly saturated blown-out white)
        glare_mask = gray >= 254
        glare_ratio = float(np.sum(glare_mask) / (width * height))
        has_glare = glare_ratio > self.glare_threshold_ratio
        if has_glare:
            issues.append(f"Specular glare detected ({glare_ratio * 100:.1f}% of document surface over-exposed)")

        # 3. Resolution Assessment
        is_low_res = width < self.min_width or height < self.min_height
        if is_low_res:
            issues.append(f"Low image resolution ({width}x{height} below minimum required {self.min_width}x{self.min_height})")

        # Compute combined quality score (0.0 to 1.0)
        # Blur contribution: min(1.0, blur_score / (blur_threshold * 2))
        blur_factor = min(1.0, blur_score / max(1.0, self.blur_threshold * 2.0))
        glare_factor = max(0.0, 1.0 - (glare_ratio / self.glare_threshold_ratio))
        res_factor = min(1.0, (width * height) / (self.min_width * self.min_height * 2.0))

        quality_score = round(float((blur_factor * 0.5) + (glare_factor * 0.3) + (res_factor * 0.2)), 2)

        status = "LOW_IMAGE_QUALITY" if issues else "PASS"

        return {
            "status": status,
            "score": quality_score,
            "issues": issues,
            "metrics": {
                "blur_score": round(blur_score, 1),
                "glare_percentage": round(glare_ratio * 100, 2),
                "width": width,
                "height": height,
            },
        }


quality_assessor = ImageQualityAssessor()
