from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.main import create_app


def test_settings_provider_chat_and_memory_persist_across_restart():
    email = f"{uuid4().hex}@example.com"
    app = create_app()
    with TestClient(app) as client:
        register = client.post(
            "/api/v1/users/register",
            json={"email": email, "password": "test-password-123"},
        )
        assert register.status_code == 200
        headers = {"Authorization": f"Bearer {register.json()['access_token']}"}

        updated_settings = client.put(
            "/api/v1/settings/",
            headers=headers,
            json={"preferred_provider": "local"},
        )
        assert updated_settings.status_code == 200
        assert updated_settings.json()["preferred_provider"] == "local"

        saved = client.post(
            "/api/v1/memory/",
            headers=headers,
            json={"key": "workflow", "value": "persist across restart"},
        )
        assert saved.status_code == 200

        with patch("backend.services.chat_service.ModelRouter.chat", return_value="mocked provider response") as chat:
            response = client.post(
                "/api/v1/chat/message",
                headers=headers,
                json={"prompt": "hello"},
            )
        assert response.status_code == 200
        assert response.json()["provider"] == "local"
        assert chat.call_args.kwargs["provider_name"] == "local"

        with patch("backend.services.chat_service.ModelRouter.chat", return_value="explicit response") as chat:
            explicit_response = client.post(
                "/api/v1/chat/message",
                headers=headers,
                json={"prompt": "use OpenAI for this request", "provider": "openai"},
            )
        assert explicit_response.status_code == 200
        assert explicit_response.json()["provider"] == "openai"
        assert chat.call_args.kwargs["provider_name"] == "openai"

    with TestClient(create_app()) as restarted_client:
        settings_response = restarted_client.get("/api/v1/settings/", headers=headers)
        memory_response = restarted_client.get(
            "/api/v1/memory/search",
            headers=headers,
            params={"query": "workflow"},
        )

    assert settings_response.json()["preferred_provider"] == "local"
    assert memory_response.status_code == 200
    assert memory_response.json()["results"][0]["value"] == "persist across restart"


def test_tauri_origin_is_allowed_for_health_and_chat_api():
    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/health",
            headers={"Origin": "http://tauri.localhost"},
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://tauri.localhost"
