import os
from pathlib import Path
import pytest

from backend.intelligence.router import ModelRouter
from backend.tools.file_tool import FileTool
from backend.tools.registry import ToolRegistry
from memory.memory_manager import MemoryManager


def test_memory_manager_persistence(tmp_path: Path):
    storage_dir = tmp_path / ".offspace"
    manager = MemoryManager(storage_dir=str(storage_dir))
    manager.save_user_preference("favorite_color", "blue")
    assert manager.get_user_preference("favorite_color") == "blue"

    manager2 = MemoryManager(storage_dir=str(storage_dir))
    assert manager2.get_user_preference("favorite_color") == "blue"


def test_tool_registry_and_file_tool(tmp_path: Path):
    registry = ToolRegistry()
    file_tool = FileTool()
    registry.register("file", file_tool)

    tool = registry.get("file")
    assert tool is not None
    assert tool.validate("create", {"path": "test.txt", "content": "hello"}) is True

    response = tool.execute("create", {"path": "test.txt", "content": "hello", "base_path": str(tmp_path)})
    assert "File created" in response
    assert (tmp_path / "test.txt").exists()


def test_model_router_invalid_provider():
    router = ModelRouter(config={"DEFAULT_PROVIDER": "local"})
    with pytest.raises(RuntimeError):
        router.chat("Hello")
