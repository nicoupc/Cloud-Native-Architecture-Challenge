"""
Token Bucket Rate Limiter

Controls the rate of notification sending to prevent throttling
of external services (email providers, APIs, etc.).
"""

import asyncio
import time
import logging

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """
    Token Bucket algorithm for rate limiting.
    
    Tokens are added at a fixed rate. Each operation consumes one token.
    If no tokens are available, the caller waits until one is replenished.
    """
    
    def __init__(self, rate: float = 5.0, max_tokens: float = 10.0):
        """
        Args:
            rate: Tokens added per second (controls sustained throughput)
            max_tokens: Maximum burst size (bucket capacity)
        """
        self.rate = rate
        self.max_tokens = max_tokens
        self._tokens = max_tokens
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        logger.info(f"Rate limiter initialized: {rate} msgs/sec, burst={max_tokens}")

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.max_tokens, self._tokens + elapsed * self.rate)
        self._last_refill = now

    async def acquire(self) -> None:
        """
        Acquire a token, waiting if necessary.
        
        This is the main method consumers call before processing a message.
        """
        async with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return
            
            # Calculate wait time for next token
            wait_time = (1.0 - self._tokens) / self.rate
            logger.debug(f"Rate limited: waiting {wait_time:.3f}s for next token")
        
        # Wait outside the lock so other coroutines aren't blocked
        await asyncio.sleep(wait_time)
        
        async with self._lock:
            self._refill()
            self._tokens -= 1.0

    @property
    def available_tokens(self) -> float:
        """Current number of available tokens (for monitoring)."""
        self._refill()
        return self._tokens
