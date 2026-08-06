import pytest
from pathlib import Path

from core.assistant import Assistant
from core.automation import AutomationManager
from core.voice import VoiceController


def test_voice_controller_detects_wake_phrase():
    controller = VoiceController()
    assert controller.contains_wake_phrase("hey offspace can you help me") is True
    assert controller.contains_wake_phrase("hello there") is False


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


@pytest.mark.asyncio
async def test_assistant_handles_voice_commands():
    assistant = Assistant()
    response = await assistant.process_command("hey offspace create a file called draft.txt")
    assert isinstance(response, str)
    assert len(response) > 0
