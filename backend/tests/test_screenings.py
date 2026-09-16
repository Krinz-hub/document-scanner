"""Tests for /api/v1/screenings API lifecycle."""


def test_create_screening_lifecycle(client):
    # 1. Create a screening
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "CP-BERLIN-01"})
    assert res.status_code == 201
    data = res.json()
    screening_id = data["id"]
    assert screening_id.startswith("SCR-")
    assert data["checkpoint_id"] == "CP-BERLIN-01"
    assert data["status"] == "PENDING"
    assert data["review_priority"] == "LOW"
    assert data["verification"]["mrz"] == "PENDING"

    # 2. List screenings
    list_res = client.get("/api/v1/screenings")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1
    assert any(s["id"] == screening_id for s in items)

    # 3. Get screening detail
    detail_res = client.get(f"/api/v1/screenings/{screening_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == screening_id
    assert detail["status"] == "PENDING"

    # 4. Get screening evidence
    evidence_res = client.get(f"/api/v1/screenings/{screening_id}/evidence")
    assert evidence_res.status_code == 200
    assert isinstance(evidence_res.json(), list)


def test_get_nonexistent_screening(client):
    res = client.get("/api/v1/screenings/SCR-NONEXISTENT-999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_record_officer_decision_and_audit(client):
    # 1. Create a screening
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "CP-TERMINAL-2"})
    assert res.status_code == 201
    screening_id = res.json()["id"]

    # 2. Officer records manual decision
    decision_payload = {
        "action": "CLEAR",
        "notes": "Physical secondary visual inspection completed. Cleared for entry.",
        "decided_by": "OFFICER-7892"
    }
    dec_res = client.post(f"/api/v1/screenings/{screening_id}/decision", json=decision_payload)
    assert dec_res.status_code == 200
    updated = dec_res.json()
    assert updated["status"] == "ACCEPTED"
    assert updated["officer_action"] == "CLEAR"
    assert updated["officer_notes"] == "Physical secondary visual inspection completed. Cleared for entry."
    assert updated["decided_by"] == "OFFICER-7892"
    assert updated["decided_at"] is not None

    # 3. Retrieve immutable audit trail
    audit_res = client.get(f"/api/v1/screenings/{screening_id}/audit")
    assert audit_res.status_code == 200
    events = audit_res.json()
    assert len(events) >= 2
    types = [e["event_type"] for e in events]
    assert "SCREENING_INITIALIZED" in types
    assert "OFFICER_DECISION_RECORDED" in types

