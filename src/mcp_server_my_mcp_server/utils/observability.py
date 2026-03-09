import time
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class FetchLog:
    url: str
    strategy: str
    status_code: int | None
    success: bool
    error_code: str | None
    retries: int
    duration_ms: int
    ua: str
    referer: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Timer:
    def __init__(self):
        self.t0 = time.time()

    def elapsed_ms(self) -> int:
        return int((time.time() - self.t0) * 1000)