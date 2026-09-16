"""Tests for Module 5: Tampering Analysis Heuristics."""

import numpy as np
import cv2
from backend.app.modules.tampering import tampering_detector


def test_tampering_clean_synthetic_document():
    # Clean continuous document image
    img = np.full((600, 800, 3), 220, dtype=np.uint8)
    # Add gentle noise
    noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)

    res = tampering_detector.analyze(img)
    assert res["overall_status"] in ("PASS", "CLEAN")
    assert all(r["status"] != "SUSPICIOUS" for r in res["results"])


def test_tampering_boundary_anomaly_detected():
    # Document with artificial high-contrast hard rectangle spliced into photo area
    img = np.full((600, 800, 3), 200, dtype=np.uint8)
    h, w = img.shape[:2]
    px, py, pw, ph = int(w * 0.08), int(h * 0.18), int(w * 0.35), int(h * 0.55)

    # Insert high-contrast black box with harsh stark borders
    cv2.rectangle(img, (px, py), (px + pw, py + ph), (0, 0, 0), thickness=-1)
    cv2.rectangle(img, (px, py), (px + pw, py + ph), (255, 255, 255), thickness=4)

    res = tampering_detector.analyze(img)
    photo_results = [r for r in res["results"] if r["region"] == "PHOTO"]
    assert any(r["status"] == "SUSPICIOUS" for r in photo_results)
    assert len(res["evidence_items"]) > 0
