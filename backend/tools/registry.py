from typing import Dict, Optional

from .interface import ToolInterface


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolInterface] = {}

    def register(self, name: str, tool: ToolInterface) -> None:
        self.tools[name.lower()] = tool

    def get(self, name: str) -> Optional[ToolInterface]:
        return self.tools.get(name.lower())

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())
