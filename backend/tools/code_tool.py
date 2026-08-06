from typing import Any, Dict

from .interface import ToolInterface


class CodeTool(ToolInterface):
    ALLOWED_ACTIONS = {"generate", "explain", "fix", "review"}

    def validate(self, action: str, payload: Dict[str, Any]) -> bool:
        return action in self.ALLOWED_ACTIONS and "code" in payload

    def execute(self, action: str, payload: Dict[str, Any]) -> str:
        code = payload["code"]
        if action == "generate":
            return f"Generated code scaffold for request: {payload.get('request', 'general code task')}"
        if action == "explain":
            return f"Explained code snippet: {code[:80]}..."
        if action == "fix":
            return f"Provided fix suggestions for code: {code[:80]}..."
        if action == "review":
            return f"Code review summary: style looks good, consider abstracting repeated logic."
        return f"Unsupported code action: {action}"
