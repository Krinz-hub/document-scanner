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
