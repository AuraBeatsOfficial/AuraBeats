"""AuraBeats - Simple token-bucket rate limiter."""
import time


class RateLimit:
    """Per-key sliding-window limiter."""

    def __init__(self, max_calls: int = 5, window: float = 10.0):
        self.max_calls = max_calls
        self.window = window
        self._hits: dict = {}  # key -> [timestamps]

    def is_allowed(self, key) -> bool:
        now = time.time()
        hits = [t for t in self._hits.get(key, []) if now - t < self.window]
        if len(hits) >= self.max_calls:
            self._hits[key] = hits
            return False
        hits.append(now)
        self._hits[key] = hits
        return True

    def remaining(self, key) -> int:
        now = time.time()
        hits = [t for t in self._hits.get(key, []) if now - t < self.window]
        return max(0, self.max_calls - len(hits))

    def reset(self, key):
        self._hits.pop(key, None)


# predefined limiters
play_limiter = RateLimit(max_calls=5, window=10.0)
search_limiter = RateLimit(max_calls=8, window=15.0)
download_limiter = RateLimit(max_calls=3, window=60.0)
