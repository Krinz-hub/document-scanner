"""Tests for Module 6: Facial Verification and Comparison."""

import numpy as np
import cv2
from backend.app.modules.face import face_engine


def make_synthetic_face_image(base_color=(180, 160, 140)) -> bytes:
    """Generate a clean synthetic portrait image with facial geometry."""
    img = np.full((300, 300, 3), 240, dtype=np.uint8)
    # Head oval
    cv2.ellipse(img, (150, 150), (60, 80), 0, 0, 360, base_color, -1)
    # Eyes
    cv2.circle(img, (130, 130), 8, (50, 40, 30), -1)
    cv2.circle(img, (170, 130), 8, (50, 40, 30), -1)
    # Nose line
    cv2.line(img, (150, 140), (150, 165), (100, 90, 80), 2)
    # Mouth
    cv2.ellipse(img, (150, 185), (20, 8), 0, 0, 180, (80, 60, 60), 2)

    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def test_face_comparison_same_person():
    face1 = make_synthetic_face_image(base_color=(180, 160, 140))
    face2 = make_synthetic_face_image(base_color=(180, 160, 140))

    res = face_engine.compare_faces(face1, face2)
    # Identical descriptor vectors should yield similarity close to 1.0
    assert res["status"] == "MATCH"
    assert res["similarity"] is not None
    assert res["similarity"] >= 0.85


def test_face_comparison_different_features():
    face1 = make_synthetic_face_image(base_color=(220, 200, 180))
    # Different face (dark silhouette with inverted geometry)
    img_diff = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(img_diff, (150, 150), 40, (20, 20, 20), -1)
    _, buf_diff = cv2.imencode(".jpg", img_diff)
    face2 = buf_diff.tobytes()

    res = face_engine.compare_faces(face1, face2)
    assert res["status"] in ("LOW_SIMILARITY", "REVIEW")
    assert res["similarity"] < 0.80
