import time
import threading


class TokenBucket:
    """
    Simple token bucket rate limiter.

    tokens: current tokens available
    capacity: max tokens
    refill_rate_per_sec: tokens added per second

    Use acquire() to block briefly until a token is available.
    """

    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = max(1, capacity)
        self.tokens = float(self.capacity)
        self.refill_rate_per_sec = float(refill_rate_per_sec)
        self.lock = threading.Lock()
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        if elapsed <= 0:
            return
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate_per_sec)
        self.last_refill = now

    def acquire(self, blocking: bool = True, wait_step: float = 0.05) -> bool:
        while True:
            with self.lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            if not blocking:
                return False
            time.sleep(wait_step)