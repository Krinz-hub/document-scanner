"""Tests for Module 1: Image Quality Assessment."""

import numpy as np
import cv2
from backend.app.modules.quality import quality_assessor


def test_quality_sharp_image():
    # Synthetic clean image with high contrast edges
    img = np.zeros((600, 800, 3), dtype=np.uint8)
    # Draw sharp grid with non-saturated white lines
    for x in range(0, 800, 40):
        cv2.line(img, (x, 0), (x, 600), (200, 200, 200), 2)
    for y in range(0, 600, 40):
        cv2.line(img, (0, y), (800, y), (200, 200, 200), 2)

    res = quality_assessor.assess(img)
    assert res["status"] == "PASS"
    assert res["score"] > 0.6
    assert len(res["issues"]) == 0


def test_quality_blurry_image():
    # Synthetic blurry image (solid gray with mild noise)
    img = np.full((600, 800, 3), 128, dtype=np.uint8)
    blurred = cv2.GaussianBlur(img, (25, 25), 0)

    res = quality_assessor.assess(blurred)
    assert res["status"] == "LOW_IMAGE_QUALITY"
    assert any("blur" in issue.lower() for issue in res["issues"])


def test_quality_glare_image():
    # Image with > 10% saturated white pixels
    img = np.full((600, 800, 3), 100, dtype=np.uint8)
    img[100:300, 100:400] = 255  # Overexposed patch

    res = quality_assessor.assess(img)
    assert res["status"] == "LOW_IMAGE_QUALITY"
    assert any("glare" in issue.lower() for issue in res["issues"])
