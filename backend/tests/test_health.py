"""Tests for /api/v1/health endpoint."""


def test_health_check_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "Border Document Screening" in data["app"]
    assert data["version"] == "1.0.0"


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs" in data
    assert data["health"] == "/api/v1/health"


def test_metrics_endpoints(client):
    res_root = client.get("/metrics")
    assert res_root.status_code == 200
    assert "border_screenings_total" in res_root.text
    assert "border_system_healthy 1" in res_root.text

    res_api = client.get("/api/v1/metrics")
    assert res_api.status_code == 200
    assert "border_screenings_total" in res_api.text

