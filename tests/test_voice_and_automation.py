import pytest
from pathlib import Path
import sys

from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

from core.assistant import Assistant
from core.automation import AutomationManager
from core.voice import VoiceController
from backend.voice.engine import VoiceEngine
import core.voice as voice_module


def test_voice_controller_detects_wake_phrase():
    controller = VoiceController()
    assert controller.contains_wake_phrase("hey offspace can you help me") is True
    assert controller.contains_wake_phrase("hello there") is False


def test_voice_controller_listen_once_uses_recognizer(monkeypatch):
    source = MagicMock()
    recognizer = Mock()
    recognizer.listen.return_value = object()
    recognizer.recognize_google.return_value = "hello offspace"
    monkeypatch.setattr(
        voice_module,
        "sr",
        SimpleNamespace(
            UnknownValueError=type("UnknownValueError", (Exception,), {}),
            RequestError=type("RequestError", (Exception,), {}),
            WaitTimeoutError=type("WaitTimeoutError", (Exception,), {}),
            Recognizer=Mock,
            Microphone=lambda: source,
        ),
    )
    controller = VoiceController()
    controller.recognizer = recognizer

    assert controller.listen_once() == "hello offspace"


def test_voice_controller_handles_recognition_service_error(monkeypatch):
    request_error = type("RequestError", (Exception,), {})
    source = MagicMock()
    recognizer = Mock()
    recognizer.listen.return_value = object()
    recognizer.recognize_google.side_effect = request_error("offline")
    monkeypatch.setattr(
        voice_module,
        "sr",
        SimpleNamespace(
            UnknownValueError=type("UnknownValueError", (Exception,), {}),
            RequestError=request_error,
            WaitTimeoutError=type("WaitTimeoutError", (Exception,), {}),
            Recognizer=Mock,
            Microphone=lambda: source,
        ),
    )
    controller = VoiceController()
    controller.recognizer = recognizer

    assert controller.listen_once() == ""


def test_voice_engine_reports_recognition_service_error(monkeypatch):
    request_error = type("RequestError", (Exception,), {})
    recognizer = Mock()
    recognizer.recognize_google.side_effect = request_error("offline")
    monkeypatch.setitem(
        sys.modules,
        "speech_recognition",
        SimpleNamespace(
            UnknownValueError=type("UnknownValueError", (Exception,), {}),
            RequestError=request_error,
            Recognizer=Mock(return_value=recognizer),
        ),
    )

    assert VoiceEngine().recognize(object()) is None


def test_automation_create_file_and_search(tmp_path: Path):
    manager = AutomationManager(base_path=str(tmp_path))
    file_path = tmp_path / "notes.txt"

    result = manager.execute_command("create file notes.txt with content hello offspace")
    assert "created" in result.lower()
    assert file_path.exists()

    search_result = manager.execute_command("search files for notes")
    assert "notes.txt" in search_result


def test_dangerous_action_requires_confirmation(tmp_path: Path):
    manager = AutomationManager(base_path=str(tmp_path))
    delete_path = tmp_path / "sensitive.txt"
    delete_path.write_text("data")

    result = manager.execute_command("delete file sensitive.txt")
    assert "confirm" in result.lower()
    assert delete_path.exists()

    confirmed = manager.execute_command("delete file sensitive.txt", confirmation="yes")
    assert "deleted" in confirmed.lower()
    assert not delete_path.exists()


def test_file_creation_cannot_escape_workspace(tmp_path: Path):
    outside = tmp_path.parent / "offspace-outside.txt"
    manager = AutomationManager(base_path=str(tmp_path))

    result = manager.execute_command("create file ../offspace-outside.txt with content blocked")

    assert "outside" in result.lower()
    assert not outside.exists()


@pytest.mark.asyncio
async def test_assistant_handles_voice_commands():
    assistant = Assistant()
    response = await assistant.process_command("hey offspace create a file called draft.txt")
    assert isinstance(response, str)
    assert len(response) > 0
