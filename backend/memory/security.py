import hashlib


class MemorySecurity:
    """Preparation layer for protecting local memory data."""

    @staticmethod
    def hash_value(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
