from .database import MemoryDatabase


class MemoryManager:
    """High-level interface for Offspace memory operations."""

    def __init__(self):
        self.db = MemoryDatabase()

    def remember(self, information, category="general"):
        self.db.save(category, information)

    def recall(self, keyword):
        return self.db.search(keyword)
