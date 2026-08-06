import os
from pathlib import Path
from typing import Any, Dict

from .interface import ToolInterface


class FileTool(ToolInterface):
    ALLOWED_ACTIONS = {"create", "read", "search", "delete"}

    def validate(self, action: str, payload: Dict[str, Any]) -> bool:
        return action in self.ALLOWED_ACTIONS and "path" in payload

    def execute(self, action: str, payload: Dict[str, Any]) -> str:
        base_path = Path(payload.get("base_path", ".")).expanduser()
        target = base_path / payload["path"]

        if action == "create":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(payload.get("content", ""), encoding="utf-8")
            return f"File created: {target}"

        if action == "read":
            if not target.exists():
                return f"File not found: {target}"
            return target.read_text(encoding="utf-8")

        if action == "search":
            pattern = payload.get("query", target.name.lower())
            matches = [str(path) for path in base_path.rglob("*") if pattern in path.name.lower()]
            return f"Matches: {', '.join(matches[:10])}" if matches else "No matching files found."

        if action == "delete":
            if not target.exists():
                return f"File not found: {target}"
            target.unlink()
            return f"File deleted: {target}"

        return f"Unsupported file action: {action}"
