import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """Orchestrates short-term and long-term memory systems with persistence."""

    def __init__(self, storage_dir: Optional[str] = None, context_window: int = 10):
        self.storage_dir = Path(storage_dir or ".offspace").expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_dir / "memory.db"
        self.short_term_memory: List[Dict[str, Any]] = []
        self.long_term_memory: Dict[str, Dict[str, Any]] = {}
        self.context_window = context_window
        self._initialize_database()
        self._load_long_term_memory()

    def _get_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS short_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    role TEXT,
                    content TEXT,
                    metadata TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    key TEXT PRIMARY KEY,
                    timestamp TEXT,
                    value TEXT,
                    category TEXT,
                    metadata TEXT
                )
                """
            )
            connection.commit()

    def _load_long_term_memory(self) -> None:
        with self._get_connection() as connection:
            rows = connection.execute("SELECT * FROM long_term_memory").fetchall()
            for row in rows:
                self.long_term_memory[row["key"]] = {
                    "timestamp": row["timestamp"],
                    "value": row["value"],
                    "category": row["category"],
                    "metadata": json.loads(row["metadata"] or "{}"),
                }

    def _persist_short_term(self, message: Dict[str, Any]) -> None:
        with self._get_connection() as connection:
            connection.execute(
                "INSERT INTO short_term_memory (timestamp, role, content, metadata) VALUES (?, ?, ?, ?)",
                (
                    message["timestamp"].isoformat(),
                    message["role"],
                    message["content"],
                    json.dumps(message["metadata"] or {}),
                ),
            )
            connection.commit()

    def _persist_long_term(self, key: str, entry: Dict[str, Any]) -> None:
        with self._get_connection() as connection:
            connection.execute(
                "REPLACE INTO long_term_memory (key, timestamp, value, category, metadata) VALUES (?, ?, ?, ?, ?)",
                (
                    key,
                    entry["timestamp"].isoformat(),
                    entry["value"],
                    entry.get("category", "general"),
                    json.dumps(entry.get("metadata", {})),
                ),
            )
            connection.commit()

    def add_to_short_term(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        message = {
            "timestamp": datetime.now(),
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        self.short_term_memory.append(message)
        if len(self.short_term_memory) > self.context_window:
            self.short_term_memory.pop(0)
        self._persist_short_term(message)
        logger.debug(f"Added to short-term memory: {role}: {content[:50]}...")

    def save_user_preference(self, key: str, value: str, category: str = "general", metadata: Optional[Dict[str, Any]] = None) -> None:
        memory_entry = {
            "timestamp": datetime.now(),
            "key": key,
            "value": value,
            "category": category,
            "metadata": metadata or {},
        }
        self.long_term_memory[key] = memory_entry
        self._persist_long_term(key, memory_entry)
        logger.info(f"Saved preference: {key} = {value}")

    def get_user_preference(self, key: str) -> Optional[str]:
        if key in self.long_term_memory:
            return self.long_term_memory[key]["value"]
        with self._get_connection() as connection:
            row = connection.execute("SELECT value FROM long_term_memory WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else None

    def search_long_term(self, query: str) -> List[Dict[str, Any]]:
        normalized = query.lower()
        return [
            item
            for item in self.long_term_memory.values()
            if normalized in item["key"].lower() or normalized in item["value"].lower()
        ]

    def get_short_term_context(self) -> List[Dict[str, Any]]:
        return list(self.short_term_memory)

    def clear_short_term(self) -> None:
        self.short_term_memory.clear()
        logger.info("Short-term memory cleared")

    def clear_long_term(self) -> None:
        self.long_term_memory.clear()
        with self._get_connection() as connection:
            connection.execute("DELETE FROM long_term_memory")
            connection.commit()
        logger.info("Long-term memory cleared")

    def clear_all_memory(self) -> None:
        self.clear_short_term()
        with self._get_connection() as connection:
            connection.execute("DELETE FROM short_term_memory")
            connection.execute("DELETE FROM long_term_memory")
            connection.commit()
        logger.info("All memory cleared")
