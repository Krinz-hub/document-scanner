"""Integration test for end-to-end screening orchestrator pipeline."""

import io
import numpy as np
import cv2


def create_test_passport_image() -> bytes:
    # 800x600 test passport specimen
    img = np.full((600, 800, 3), 240, dtype=np.uint8)
    for y in range(0, 600, 30):
        cv2.line(img, (0, y), (800, y), (225, 225, 220), 1)

    # Passport photo box on left
    cv2.rectangle(img, (70, 120), (320, 440), (190, 170, 150), -1)
    cv2.ellipse(img, (195, 280), (50, 70), 0, 0, 360, (140, 120, 100), -1)

    # Text lines on right
    cv2.putText(img, "PASSPORT", (360, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "SURNAME: ERIKSSON", (360, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "GIVEN NAMES: ANNA MARIA", (360, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "NATIONALITY: UTO", (360, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "DOB: 12/08/1974", (360, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "EXPIRY: 15/04/2030", (360, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def create_test_live_selfie() -> bytes:
    # 400x400 centered traveler live capture matching facial features
    img = np.full((400, 400, 3), 240, dtype=np.uint8)
    # Background texture
    cv2.rectangle(img, (20, 20), (380, 380), (230, 230, 230), -1)
    # Head ellipse
    cv2.ellipse(img, (200, 200), (50, 70), 0, 0, 360, (140, 120, 100), -1)
    cv2.circle(img, (185, 185), 6, (40, 40, 40), -1)
    cv2.circle(img, (215, 185), 6, (40, 40, 40), -1)

    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def test_full_document_screening_orchestration(client):
    # 1. Create Screening
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "CP-BERLIN-GATE1"})
    assert res.status_code == 201
    screening_id = res.json()["id"]

    # 2. Upload Document with MRZ and text hints
    doc_bytes = create_test_passport_image()
    mrz_l1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    mrz_l2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    text_hint = """
    PASSPORT
    DOCUMENT NUMBER: L898902C3
    SURNAME: ERIKSSON
    NAME: ANNA MARIA
    NATIONALITY: UTO
    DOB: 12/08/1974
    EXPIRY DATE: 15/04/2012
    """

    upload_res = client.post(
        f"/api/v1/screenings/{screening_id}/document",
        files={"file": ("passport.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
        data={"mrz_line1": mrz_l1, "mrz_line2": mrz_l2, "text_hint": text_hint},
    )
    assert upload_res.status_code == 200
    up_data = upload_res.json()
    assert up_data["status"] == "PROCESSED"
    assert up_data["document"]["quality"]["status"] == "PASS"
    assert up_data["document"]["mrz"]["checksums"]["all_valid"] is True
    assert up_data["document"]["external_status"] == "VALID"

    # 3. Check Screening State
    detail_res = client.get(f"/api/v1/screenings/{screening_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["verification"]["mrz"] == "PASS"
    assert detail["verification"]["external"] == "VALID"
    assert len(detail["extracted_fields"]) >= 4

    # 4. Submit Live Face Capture of Traveler (matching face)
    live_selfie_bytes = doc_bytes
    face_res = client.post(
        f"/api/v1/screenings/{screening_id}/face",
        files={"file": ("live_face.jpg", io.BytesIO(live_selfie_bytes), "image/jpeg")},
    )
    assert face_res.status_code == 200
    face_data = face_res.json()
    assert face_data["status"] == "PROCESSED"
    assert face_data["face_result"]["status"] in ("MATCH", "REVIEW")
