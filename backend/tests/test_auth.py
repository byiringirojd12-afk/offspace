from fastapi.testclient import TestClient

from backend.main import create_app


def test_register_login_cycle():
    app = create_app()
    with TestClient(app) as client:
        register_response = client.post(
            "/api/v1/users/register",
            json={"email": "test@example.com", "password": "secret123", "full_name": "Test User"},
        )
        assert register_response.status_code == 200
        assert "access_token" in register_response.json()

        login_response = client.post(
            "/api/v1/users/login",
            json={"email": "test@example.com", "password": "secret123"},
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
