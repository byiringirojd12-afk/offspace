from pathlib import Path
from typing import Any, Dict, List


class VectorStore:
    def __init__(self, storage_dir: str = ".offspace"):
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index: List[Dict[str, Any]] = []

    def add(self, text: str, metadata: Dict[str, Any]) -> None:
        self.index.append({"text": text, "metadata": metadata})

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        normalized = query.lower()
        matches = [item for item in self.index if normalized in item["text"].lower()]
        return matches[:max_results]
