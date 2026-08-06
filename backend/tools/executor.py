from typing import Any, Dict

from .interface import ToolInterface
from .registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, action: str, payload: Dict[str, Any]) -> str:
        tool = self.registry.get(tool_name)
        if tool is None:
            return f"Tool '{tool_name}' is not registered."
        if not tool.validate(action, payload):
            return f"Action '{action}' is not valid for tool '{tool_name}'."
        return tool.execute(action, payload)
