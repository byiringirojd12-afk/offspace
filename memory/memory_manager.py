import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """Orchestrates short-term and long-term memory systems"""
    
    def __init__(self):
        self.short_term_memory: List[Dict] = []
        self.long_term_memory: Dict[str, Dict] = {}
        self.context_window = 10
    
    def add_to_short_term(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        message = {
            "timestamp": datetime.now(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.short_term_memory.append(message)
        if len(self.short_term_memory) > self.context_window:
            self.short_term_memory.pop(0)
        logger.debug(f"Added to short-term memory: {role}: {content[:50]}...")
    
    def save_user_preference(self, key: str, value: str, category: str = "general") -> None:
        memory_entry = {
            "timestamp": datetime.now(),
            "key": key,
            "value": value,
            "category": category
        }
        self.long_term_memory[key] = memory_entry
        logger.info(f"Saved preference: {key} = {value}")
    
    def get_user_preference(self, key: str) -> Optional[str]:
        if key in self.long_term_memory:
            return self.long_term_memory[key]["value"]
        return None
    
    def get_short_term_context(self) -> List[Dict]:
        return self.short_term_memory.copy()
    
    def clear_short_term(self) -> None:
        self.short_term_memory.clear()
        logger.info("Short-term memory cleared")
