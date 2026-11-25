from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import openai
import httpx2
import pytest
import requests

from backend.config.settings import Settings
from backend.intelligence.provider import LocalModelProvider, OpenAIProvider


def test_openai_provider_reports_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OFFSPACE_OPENAI_API_KEY", raising=False)
    provider = OpenAIProvider(api_key=None)
    assert provider.available() is False
    with pytest.raises(RuntimeError, match="API key"):
        provider.chat("hello")


@patch("openai.OpenAI")
def test_openai_provider_uses_chat_completions(mock_client):
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "real response"
    mock_client.return_value.chat.completions.create.return_value = mock_response

    provider = OpenAIProvider(api_key="test-key")

    assert provider.chat("hello") == "real response"
    mock_client.assert_called_once_with(api_key="test-key", timeout=30.0)
    mock_client.return_value.chat.completions.create.assert_called_once()
    assert mock_client.return_value.chat.completions.create.call_args.kwargs["model"] == "gpt-3.5-turbo"


@patch("openai.OpenAI")
def test_openai_provider_uses_offspace_key_alias_and_requested_model(mock_client, monkeypatch):
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "model response"
    mock_client.return_value.chat.completions.create.return_value = mock_response
    monkeypatch.setenv("OFFSPACE_OPENAI_API_KEY", "local-test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    provider = OpenAIProvider()
    assert provider.chat("hello", model="configured-model") == "model response"
    mock_client.assert_called_once_with(api_key="local-test-key", timeout=30.0)
    assert mock_client.return_value.chat.completions.create.call_args.kwargs["model"] == "configured-model"


@patch("openai.OpenAI")
def test_openai_provider_maps_timeout_without_leaking_credentials(mock_client):
    request = httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")
    mock_client.side_effect = openai.APITimeoutError(request=request)
    provider = OpenAIProvider(api_key="not-a-real-secret")

    with pytest.raises(RuntimeError, match="timed out") as error:
        provider.chat("hello")

    assert "not-a-real-secret" not in str(error.value)


@patch("openai.OpenAI")
def test_openai_provider_maps_invalid_credentials(mock_client):
    request = httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx2.Response(401, request=request)
    mock_client.side_effect = openai.AuthenticationError(
        "invalid",
        response=response,
        body=None,
    )

    with pytest.raises(RuntimeError, match="authentication failed"):
        OpenAIProvider(api_key="not-a-real-secret").chat("hello")


@patch("openai.OpenAI")
def test_openai_provider_maps_api_status_errors(mock_client):
    request = httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx2.Response(429, request=request)
    mock_client.side_effect = openai.APIStatusError(
        "provider error",
        response=response,
        body={"secret": "must not appear"},
    )

    with pytest.raises(RuntimeError, match="status 429") as error:
        OpenAIProvider(api_key="not-a-real-secret").chat("hello")

    assert "must not appear" not in str(error.value)


@patch("openai.OpenAI")
def test_openai_provider_reports_unavailable_model(mock_client):
    request = httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx2.Response(404, request=request)
    mock_client.side_effect = openai.APIStatusError(
        "not found",
        response=response,
        body={"secret": "must not appear"},
    )

    with pytest.raises(RuntimeError, match="model or endpoint was not found") as error:
        OpenAIProvider(api_key="not-a-real-secret").chat("hello")

    assert "must not appear" not in str(error.value)


def test_settings_reads_template_openai_environment_name():
    with TemporaryDirectory() as temp_dir:
        env_file = Path(temp_dir) / ".env"
        env_file.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")

        assert Settings(_env_file=env_file).openai_api_key == "test-key"


def test_settings_reads_offspace_openai_environment_name():
    with TemporaryDirectory() as temp_dir:
        env_file = Path(temp_dir) / ".env"
        env_file.write_text("OFFSPACE_OPENAI_API_KEY=test-key\n", encoding="utf-8")

        assert Settings(_env_file=env_file).openai_api_key == "test-key"


@patch("requests.post")
@patch("requests.get")
def test_local_provider_selects_requested_model(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    response = Mock()
    response.json.return_value = {"message": {"content": "local response"}}
    mock_post.return_value = response
    provider = LocalModelProvider(model="default-model")

    assert provider.chat("hello", model="selected-model") == "local response"
    assert mock_post.call_args.kwargs["json"]["model"] == "selected-model"


@patch("requests.get")
def test_local_provider_unavailable(mock_get):
    mock_get.side_effect = __import__("requests").RequestException("offline")
    provider = LocalModelProvider()
    assert provider.available() is False


@patch("requests.post")
@patch("requests.get")
def test_local_provider_reports_missing_model_without_server_details(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    response = Mock()
    missing_model_response = requests.Response()
    missing_model_response.status_code = 404
    response.raise_for_status.side_effect = requests.HTTPError(
        "404 Client Error: Not Found for url: http://127.0.0.1:11434/api/chat",
        response=missing_model_response,
    )
    mock_post.return_value = response
    provider = LocalModelProvider(model="missing-model")

    with pytest.raises(RuntimeError, match=r"ollama pull missing-model") as error:
        provider.chat("hello")

    assert "127.0.0.1" not in str(error.value)


@patch("requests.get")
def test_router_explains_how_to_start_unavailable_ollama(mock_get):
    from backend.intelligence.router import ModelRouter

    mock_get.side_effect = requests.ConnectionError("offline")

    with pytest.raises(RuntimeError, match=r"ollama serve"):
        ModelRouter({"DEFAULT_PROVIDER": "local"}).chat("hello", provider_name="local")
