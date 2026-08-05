from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MemoryType(Enum):
    USER = "user"
    CONVERSATION = "conversation"
    PREFERENCE = "preference"
    TASK = "task"
    KNOWLEDGE = "knowledge"


@dataclass
class MemoryItem:
    content: str
    memory_type: MemoryType = MemoryType.KNOWLEDGE
    importance: int = 1
    created_at: str = datetime.now().isoformat()
    last_accessed: str = datetime.now().isoformat()
