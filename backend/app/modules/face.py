"""Module 6: Facial Verification and Comparison Engine."""

from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np
from backend.app.config import get_settings

settings = get_settings()


class FaceVerificationEngine:
    VERSION = "face-compare-baseline-v1"

    def __init__(self, similarity_threshold: Optional[float] = None):
        self.threshold = similarity_threshold or settings.FACE_SIMILARITY_THRESHOLD

    def detect_face(self, image: np.ndarray, is_document: bool = False) -> Tuple[int, int, int, int]:
        """Locate face bounding box [x, y, w, h] using contour geometry with passport quadrant fallback."""
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        target_x = int(w * 0.22) if is_document else w // 2
        target_y = int(h * 0.45) if is_document else h // 2

        best_box = None
        min_dist = float("inf")

        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            # Skip contours matching the full viewport border
            if cw >= (w - 4) and ch >= (h - 4):
                continue
            ratio = ch / max(1, cw)
            if 0.7 <= ratio <= 2.5 and cw > (w * 0.10) and ch > (h * 0.12):
                dist = (x + cw // 2 - target_x) ** 2 + (y + ch // 2 - target_y) ** 2
                if dist < min_dist:
                    min_dist = dist
                    best_box = (int(x), int(y), int(cw), int(ch))

        if best_box:
            return best_box

        if is_document:
            return (int(w * 0.08), int(h * 0.18), int(w * 0.35), int(h * 0.55))

        # Fallback to center frame (50% of viewport)
        return (int(w * 0.25), int(h * 0.2), int(w * 0.5), int(h * 0.6))

    def compute_face_descriptor(self, face_crop: np.ndarray) -> np.ndarray:
        """Compute spatial gradient orientation and intensity histogram descriptor."""
        resized = cv2.resize(face_crop, (64, 64))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(resized.shape) == 3 else resized

        # 1. Gradient orientation histogram across 4x4 spatial cells
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag, ang = cv2.cartToPolar(gx, gy, angleInDegrees=True)

        cell_features = []
        # Divide into 4x4 grid (16 cells of 16x16 pixels)
        for cy in range(0, 64, 16):
            for cx in range(0, 64, 16):
                cell_mag = mag[cy : cy + 16, cx : cx + 16]
                cell_ang = ang[cy : cy + 16, cx : cx + 16]

                # 8-bin orientation histogram
                hist, _ = np.histogram(cell_ang, bins=8, range=(0, 360), weights=cell_mag)
                norm = np.linalg.norm(hist) + 1e-6
                cell_features.extend(hist / norm)

        # 2. Global intensity histogram (16 bins)
        global_hist, _ = np.histogram(gray, bins=16, range=(0, 256))
        global_hist = global_hist / (np.linalg.norm(global_hist) + 1e-6)

        feat = np.concatenate([np.array(cell_features), global_hist])
        return feat / (np.linalg.norm(feat) + 1e-6)

    def compare_faces(
        self, doc_image_bytes: bytes, live_image_bytes: bytes
    ) -> Dict[str, Any]:
        """Compare document portrait against live traveler capture."""
        doc_np = np.frombuffer(doc_image_bytes, np.uint8)
        live_np = np.frombuffer(live_image_bytes, np.uint8)

        doc_img = cv2.imdecode(doc_np, cv2.IMREAD_COLOR)
        live_img = cv2.imdecode(live_np, cv2.IMREAD_COLOR)

        if doc_img is None or live_img is None:
            return {
                "status": "LOW_FACE_QUALITY",
                "similarity": 0.0,
                "quality": 0.0,
                "model_version": self.VERSION,
                "explanation": "Could not decode face image bytes",
            }

        # Locate face crops
        dx, dy, dw, dh = self.detect_face(doc_img, is_document=True)
        lx, ly, lw, lh = self.detect_face(live_img, is_document=False)

        doc_crop = doc_img[dy : dy + dh, dx : dx + dw]
        live_crop = live_img[ly : ly + lh, lx : lx + lw]

        if doc_crop.size == 0 or live_crop.size == 0:
            return {
                "status": "NO_FACE_DETECTED",
                "similarity": 0.0,
                "quality": 0.0,
                "model_version": self.VERSION,
                "explanation": "Failed to crop face region from image",
            }

        # Quality blur check
        doc_blur = float(cv2.Laplacian(cv2.cvtColor(doc_crop, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
        live_blur = float(cv2.Laplacian(cv2.cvtColor(live_crop, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())

        # Compute descriptors
        desc_doc = self.compute_face_descriptor(doc_crop)
        desc_live = self.compute_face_descriptor(live_crop)

        # Cosine similarity: dot product of normalized descriptors
        cosine_sim = float(np.dot(desc_doc, desc_live))
        similarity = round(max(0.0, min(1.0, cosine_sim)), 3)

        # Decision threshold evaluation
        if similarity >= self.threshold:
            status = "MATCH"
            explanation = f"Face comparison score ({similarity}) meets verification threshold ({self.threshold})"
        elif similarity >= (self.threshold - 0.15):
            status = "REVIEW"
            explanation = f"Face comparison score ({similarity}) is borderline. Manual officer inspection required"
        else:
            status = "LOW_SIMILARITY"
            explanation = f"Face comparison score ({similarity}) is below match threshold ({self.threshold})"

        return {
            "status": status,
            "similarity": similarity,
            "quality": round(min(1.0, max(0.1, min(doc_blur, live_blur) / 100.0)), 2),
            "model_version": self.VERSION,
            "explanation": explanation,
            "doc_face_box": [dx, dy, dw, dh],
            "live_face_box": [lx, ly, lw, lh],
        }


face_engine = FaceVerificationEngine()
