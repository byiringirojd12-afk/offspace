from abc import ABC, abstractmethod
from typing import Any, Dict


class ToolInterface(ABC):
    @abstractmethod
    def execute(self, action: str, payload: Dict[str, Any]) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate(self, action: str, payload: Dict[str, Any]) -> bool:
        raise NotImplementedError
