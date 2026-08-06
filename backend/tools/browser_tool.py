from typing import Any, Dict

from .interface import ToolInterface


class BrowserTool(ToolInterface):
    ALLOWED_ACTIONS = {"search", "open"}

    def validate(self, action: str, payload: Dict[str, Any]) -> bool:
        return action in self.ALLOWED_ACTIONS and "query" in payload

    def execute(self, action: str, payload: Dict[str, Any]) -> str:
        query = payload["query"]
        if action == "search":
            return f"Searching the web for: {query} (simulated)"
        if action == "open":
            return f"Would open browser page for: {query}"
        return f"Unsupported browser action: {action}"
