"""Tests for Phase 12: Security, Authentication, RBAC, and Audit events."""

from backend.app.auth import hash_identifier


def test_hash_identifier_one_way():
    doc1 = "P12345678"
    hash1 = hash_identifier(doc1)
    hash2 = hash_identifier(doc1)
    hash_diff = hash_identifier("P87654321")

    assert len(hash1) == 64  # SHA-256 hex string
    assert hash1 == hash2    # Deterministic
    assert hash1 != hash_diff
    assert doc1 not in hash1  # Raw number is obscured


def test_rbac_officer_cannot_purge_retention(client):
    # Officer role attempting supervisor maintenance action
    headers = {"Authorization": "Bearer officer-token-secret"}
    res = client.post("/api/v1/maintenance/retention/purge", headers=headers)
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]


def test_rbac_supervisor_can_purge_retention(client):
    headers = {"Authorization": "Bearer supervisor-token-secret"}
    res = client.post("/api/v1/maintenance/retention/purge", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert "supervisor" in data["actor"]


def test_invalid_token_rejected(client):
    headers = {"Authorization": "Bearer invalid-fake-token"}
    res = client.post("/api/v1/maintenance/retention/purge", headers=headers)
    assert res.status_code == 401
    assert "Invalid authentication token" in res.json()["detail"]


def test_audit_trail_recorded_on_decision(client):
    # 1. Create screening
    res = client.post("/api/v1/screenings", json={"checkpoint_id": "CP-AUDIT-LANE"})
    sid = res.json()["id"]

    # 2. Record manual decision
    dec_res = client.post(
        f"/api/v1/screenings/{sid}/decision",
        json={"action": "ACCEPTED", "notes": "Passenger documents verified manually", "officer_id": "OFFICER-77"},
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "ACCEPTED"
    assert dec_res.json()["officer_action"] == "ACCEPTED"

    # 3. Retrieve immutable audit trail
    audit_res = client.get(f"/api/v1/screenings/{sid}/audit")
    assert audit_res.status_code == 200
    events = audit_res.json()
    assert len(events) >= 2
    event_types = [e["event_type"] for e in events]
    assert "SCREENING_INITIALIZED" in event_types
    assert "OFFICER_DECISION_RECORDED" in event_types
