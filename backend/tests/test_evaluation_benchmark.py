"""Phase 13: End-to-End Evaluation, Latency Benchmarks, and Failure Sets."""

import time
import io
import numpy as np
import cv2


def generate_specimen_document(blur: bool = False, glare: bool = False) -> bytes:
    """Generate controlled test documents for benchmark evaluation."""
    img = np.full((600, 800, 3), 235, dtype=np.uint8)
    for y in range(0, 600, 30):
        cv2.line(img, (0, y), (800, y), (215, 215, 210), 1)

    # Portrait area
    cv2.rectangle(img, (70, 120), (320, 440), (190, 170, 150), -1)
    cv2.ellipse(img, (195, 280), (50, 70), 0, 0, 360, (140, 120, 100), -1)

    # Typography
    cv2.putText(img, "PASSPORT", (360, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "DOCUMENT NUMBER: L898902C3", (360, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "SURNAME: ERIKSSON", (360, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "NAME: ANNA MARIA", (360, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "NATIONALITY: UTO", (360, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "DOB: 12/08/1974", (360, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "EXPIRY DATE: 15/04/2012", (360, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    if blur:
        img = cv2.GaussianBlur(img, (35, 35), 0)
    if glare:
        img[100:350, 200:500] = 255

    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def test_clean_document_evaluation(client):
    """Step 89: Clean document test set."""
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "BENCHMARK-CLEAN"})
    sid = res.json()["id"]

    doc_bytes = generate_specimen_document(blur=False, glare=False)
    mrz_l1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    mrz_l2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<10"

    up = client.post(
        f"/api/v1/screenings/{sid}/document",
        files={"file": ("clean.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
        data={"mrz_line1": mrz_l1, "mrz_line2": mrz_l2},
    )
    assert up.status_code == 200
    assert up.json()["document"]["quality"]["status"] == "PASS"
    assert up.json()["document"]["mrz"]["checksums"]["all_valid"] is True


def test_altered_document_evaluation(client):
    """Step 90: Altered document test set (corrupted checksum and tamper anomaly)."""
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "BENCHMARK-ALTERED"})
    sid = res.json()["id"]

    doc_bytes = generate_specimen_document()
    # Bad MRZ checksum digit '9' instead of '6'
    mrz_corrupted_l2 = "L898902C39UTO7408122F1204159ZE184226B<<<<<10"

    up = client.post(
        f"/api/v1/screenings/{sid}/document",
        files={"file": ("altered.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
        data={
            "mrz_line1": "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
            "mrz_line2": mrz_corrupted_l2,
        },
    )
    assert up.status_code == 200

    detail = client.get(f"/api/v1/screenings/{sid}").json()
    assert detail["status"] == "REVIEW_REQUIRED"
    assert detail["review_priority"] == "HIGH"
    assert detail["verification"]["mrz"] == "FAIL"
    assert any("mrz" in r.lower() for r in detail["reasons"])


def test_low_quality_document_evaluation(client):
    """Step 91: Low-quality document test set (blurry image rejected/flagged)."""
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "BENCHMARK-BLUR"})
    sid = res.json()["id"]

    blurry_bytes = generate_specimen_document(blur=True)
    up = client.post(
        f"/api/v1/screenings/{sid}/document",
        files={"file": ("blur.jpg", io.BytesIO(blurry_bytes), "image/jpeg")},
    )
    assert up.status_code == 200
    assert up.json()["document"]["quality"]["status"] == "LOW_IMAGE_QUALITY"


def test_face_match_and_mismatch_evaluation(client):
    """Step 92: Face match / non-match evaluation."""
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "BENCHMARK-FACE"})
    sid = res.json()["id"]

    doc_bytes = generate_specimen_document()
    client.post(
        f"/api/v1/screenings/{sid}/document",
        files={"file": ("doc.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
    )

    # 1. Matching face
    match_res = client.post(
        f"/api/v1/screenings/{sid}/face",
        files={"file": ("same.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
    ).json()
    assert match_res["face_result"]["status"] in ("MATCH", "REVIEW")
    assert match_res["face_result"]["similarity"] >= 0.70

    # 2. Non-matching face (black block)
    diff_img = np.zeros((300, 300, 3), dtype=np.uint8)
    _, d_buf = cv2.imencode(".jpg", diff_img)
    mismatch_res = client.post(
        f"/api/v1/screenings/{sid}/face",
        files={"file": ("diff.jpg", io.BytesIO(d_buf.tobytes()), "image/jpeg")},
    ).json()
    assert mismatch_res["face_result"]["status"] == "LOW_SIMILARITY"


def test_external_service_outage_evaluation(client):
    """Step 93: External service failure resilience (UNAVAILABLE != VALID)."""
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "BENCHMARK-OUTAGE"})
    sid = res.json()["id"]

    doc_bytes = generate_specimen_document()
    # Number containing 'TIMEOUT' triggers simulated registry failure
    up = client.post(
        f"/api/v1/screenings/{sid}/document",
        files={"file": ("doc.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
        data={"text_hint": "DOCUMENT NUMBER: TIMEOUT-9999\nNATIONALITY: UTO"},
    )
    assert up.status_code == 200
    assert up.json()["document"]["external_status"] == "UNAVAILABLE"

    detail = client.get(f"/api/v1/screenings/{sid}").json()
    # Critical: UNAVAILABLE must never be mapped to VALID
    assert detail["verification"]["external"] == "UNAVAILABLE"


def test_module_failure_resilience(client):
    """Step 94: Malformed file inputs fail gracefully without 500 crashes."""
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "BENCHMARK-CRASH"})
    sid = res.json()["id"]

    # Unsupported format
    bad_res = client.post(
        f"/api/v1/screenings/{sid}/document",
        files={"file": ("malicious.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload")},
    )
    assert bad_res.status_code == 400
    assert "Invalid file type" in bad_res.json()["detail"]


def test_end_to_end_latency_benchmark(client):
    """Step 95: Verify end-to-end pipeline executes under latency SLA (< 1.5s)."""
    start_time = time.perf_counter()

    # 1. Create
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "BENCHMARK-LATENCY"})
    sid = res.json()["id"]

    # 2. Ingest Document
    doc_bytes = generate_specimen_document()
    client.post(
        f"/api/v1/screenings/{sid}/document",
        files={"file": ("doc.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
        data={
            "mrz_line1": "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
            "mrz_line2": "L898902C36UTO7408122F1204159ZE184226B<<<<<10",
        },
    )

    # 3. Biometric Compare
    client.post(
        f"/api/v1/screenings/{sid}/face",
        files={"file": ("face.jpg", io.BytesIO(doc_bytes), "image/jpeg")},
    )

    # 4. View Detail
    detail = client.get(f"/api/v1/screenings/{sid}").json()
    total_elapsed = time.perf_counter() - start_time

    assert detail["id"] == sid
    # Assert execution completed in under 1.5 seconds
    assert total_elapsed < 1.5
    print(f"\n[LATENCY BENCHMARK] Full screening pipeline completed in {total_elapsed * 1000:.1f}ms")
