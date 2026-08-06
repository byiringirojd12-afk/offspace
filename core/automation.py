import logging
import shlex
import subprocess
from pathlib import Path
from typing import Dict, Optional

from .security import PermissionManager

logger = logging.getLogger(__name__)


class AutomationManager:
    """Safe computer automation helpers with confirmation gating for dangerous actions."""

    DANGEROUS_ACTIONS = {"delete", "overwrite", "shutdown", "format"}
    APPLICATION_ACTIONS = {"open application", "open app", "launch"}

    def __init__(self, base_path: str = ".") -> None:
        self.base_path = Path(base_path).resolve()
        self.confirmations: Dict[str, bool] = {}
        self.permission_manager = PermissionManager()
        self.action_log: list[str] = []

    def _normalize(self, text: str) -> str:
        return " ".join(text.lower().strip().split())

    def _parse_target(self, text: str) -> Optional[str]:
        cleaned = self._normalize(text)
        token_index = cleaned.find("file ")
        if token_index == -1:
            return None
        remainder = cleaned[token_index + len("file "):]
        if " with content " in remainder:
            remainder = remainder.split(" with content ", 1)[0]
        if " for " in remainder:
            remainder = remainder.split(" for ", 1)[0]
        if " to " in remainder:
            remainder = remainder.split(" to ", 1)[0]
        return remainder.strip()

    def _get_content(self, text: str) -> Optional[str]:
        cleaned = self._normalize(text)
        if " with content " not in cleaned:
            return None
        return cleaned.split(" with content ", 1)[1].strip()

    def _log_action(self, message: str) -> None:
        logger.info(message)
        self.action_log.append(message)

    def execute_command(self, command: str, confirmation: Optional[str] = None) -> str:
        normalized = self._normalize(command)
        self._log_action(f"Executing automation command: {normalized}")

        if any(action in normalized for action in self.APPLICATION_ACTIONS):
            return "Application launch request received. Please confirm the app name to open."

        if "create file" in normalized:
            target = self._parse_target(normalized) or "untitled.txt"
            content = self._get_content(normalized) or ""
            file_path = self.base_path / target
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return f"Created file: {file_path}"

        if "search files" in normalized:
            query = normalized.split("search files for", 1)[-1].strip()
            matches = [str(path.name) for path in self.base_path.rglob("*") if query in path.name.lower()]
            if not matches:
                return f"No files found matching '{query}'"
            return f"Files found: {', '.join(matches[:5])}"

        if "run developer tools" in normalized:
            return "Developer tools launch request received. Please confirm the tool to run."

        if any(action in normalized for action in self.DANGEROUS_ACTIONS):
            action_name = next(action for action in self.DANGEROUS_ACTIONS if action in normalized)
            if confirmation not in {"yes", "y", "confirm"}:
                return f"Dangerous action detected: {action_name}. Please confirm by saying 'yes' to continue."
            if not self.permission_manager.has_permission(action_name):
                self.permission_manager.request_permission(action_name)

            target = self._parse_target(normalized)
            if target:
                file_path = self.base_path / target
                if file_path.exists():
                    file_path.unlink()
                    return f"Deleted file: {file_path}"
                return f"Target file not found: {file_path}"
            return f"Unable to parse target for dangerous action: {action_name}."

        if "run shell" in normalized or "execute" in normalized:
            if not self.permission_manager.has_permission("shell"):
                return "Shell execution permission is denied."
            try:
                command_text = command.split("execute", 1)[-1].strip() if "execute" in normalized else command
                result = subprocess.run(
                    shlex.split(command_text),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                output = result.stdout.strip() or result.stderr.strip() or "Command executed."
                return f"Shell output: {output}"
            except Exception as exc:
                return f"Shell execution failed: {exc}"

        return f"Command not recognized: {command}"

    def get_action_log(self) -> list[str]:
        return list(self.action_log)

    def clear_action_log(self) -> None:
        self.action_log.clear()

    def request_permission(self, action: str) -> bool:
        return self.permission_manager.request_permission(action)
