import subprocess
from typing import Any, Dict

from .interface import ToolInterface


class SystemTool(ToolInterface):
    ALLOWED_ACTIONS = {"run", "shell"}

    def validate(self, action: str, payload: Dict[str, Any]) -> bool:
        return action in self.ALLOWED_ACTIONS and "command" in payload

    def execute(self, action: str, payload: Dict[str, Any]) -> str:
        try:
            result = subprocess.run(
                payload["command"],
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip() or result.stderr.strip() or "Command executed."
        except Exception as exc:
            return f"System execution failed: {exc}"
