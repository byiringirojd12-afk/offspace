from fastapi.testclient import TestClient

from backend.main import create_app


def test_health_endpoint():
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["database"] == "connected"
    assert response.json()["version"] == "1.0.0"
