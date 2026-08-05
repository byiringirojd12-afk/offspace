import sqlite3
from pathlib import Path


class MemoryDatabase:
    """SQLite persistence layer for Offspace memory."""

    def __init__(self, db_path="data/offspace_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.initialize()

    def initialize(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

    def save(self, category, content):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO memories(category, content) VALUES (?, ?)",
            (category, content)
        )
        self.connection.commit()

    def search(self, keyword):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM memories WHERE content LIKE ?",
            (f"%{keyword}%",)
        )
        return cursor.fetchall()
