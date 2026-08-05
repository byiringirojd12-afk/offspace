"""File automation tools for Offspace."""

from pathlib import Path


class FileController:
    """Basic file operations with safe path handling."""

    def exists(self, path: str):
        return Path(path).exists()

    def list_directory(self, path: str = "."):
        return [item.name for item in Path(path).iterdir()]
