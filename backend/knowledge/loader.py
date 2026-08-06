import os
from pathlib import Path
from typing import List


class DocumentLoader:
    SUPPORTED_EXTENSIONS = {"txt", "md", "py", "json"}

    def __init__(self, source_dir: str = "."):
        self.source_dir = Path(source_dir).expanduser()

    def load_documents(self) -> List[str]:
        documents: List[str] = []
        for path in self.source_dir.rglob("*"):
            if path.is_file() and path.suffix.lstrip(".").lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    documents.append(path.read_text(encoding="utf-8"))
                except OSError:
                    continue
        return documents
