import time
import hashlib
from typing import Any, Dict, Optional


class TTLCache:
    """A tiny TTL cache with string keys."""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self.store: Dict[str, Any] = {}
        self.expire: Dict[str, float] = {}

    def _now(self) -> float:
        return time.time()

    def set(self, key: str, value: Any):
        self.store[key] = value
        self.expire[key] = self._now() + self.ttl

    def get(self, key: str) -> Optional[Any]:
        v = self.store.get(key)
        if v is None:
            return None
        if self.expire.get(key, 0) < self._now():
            # expired
            self.delete(key)
            return None
        return v

    def delete(self, key: str):
        self.store.pop(key, None)
        self.expire.pop(key, None)


def content_fingerprint(text: str) -> str:
    """Return a short fingerprint of content for de-duplication."""
    h = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
    return h[:16]