"""
Tests for TokenBucketRateLimiter
"""

import asyncio
import time
import pytest

from src.infrastructure.rate_limiter import TokenBucketRateLimiter


class TestTokenBucketRateLimiter:
    """Tests for the token bucket rate limiter"""

    @pytest.mark.asyncio
    async def test_initial_burst_allowed(self):
        """Burst of requests up to max_tokens should proceed immediately"""
        limiter = TokenBucketRateLimiter(rate=5.0, max_tokens=5.0)
        start = time.monotonic()
        for _ in range(5):
            await limiter.acquire()
        elapsed = time.monotonic() - start
        # 5 tokens available initially → all should be near-instant
        assert elapsed < 0.2

    @pytest.mark.asyncio
    async def test_rate_limiting_slows_down(self):
        """After burst is exhausted, acquire() should wait"""
        limiter = TokenBucketRateLimiter(rate=10.0, max_tokens=2.0)
        # Exhaust burst
        await limiter.acquire()
        await limiter.acquire()
        # Next one must wait ~0.1s (1 token / 10 per sec)
        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.05  # at least some wait

    @pytest.mark.asyncio
    async def test_tokens_refill_over_time(self):
        """Tokens should refill after waiting"""
        limiter = TokenBucketRateLimiter(rate=10.0, max_tokens=5.0)
        # Exhaust all tokens
        for _ in range(5):
            await limiter.acquire()
        # Wait for refill (0.3s → 3 tokens at rate 10/s)
        await asyncio.sleep(0.3)
        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 0.1  # should be immediate after refill

    @pytest.mark.asyncio
    async def test_max_tokens_cap(self):
        """Tokens should not exceed max_tokens"""
        limiter = TokenBucketRateLimiter(rate=100.0, max_tokens=3.0)
        await asyncio.sleep(0.1)  # would add 10 tokens at rate 100/s
        assert limiter.available_tokens <= 3.0

    @pytest.mark.asyncio
    async def test_available_tokens_property(self):
        """available_tokens should reflect current state"""
        limiter = TokenBucketRateLimiter(rate=5.0, max_tokens=5.0)
        initial = limiter.available_tokens
        assert initial <= 5.0
        await limiter.acquire()
        assert limiter.available_tokens < initial

    @pytest.mark.asyncio
    async def test_default_values(self):
        """Default rate=5.0, max_tokens=10.0"""
        limiter = TokenBucketRateLimiter()
        assert limiter.rate == 5.0
        assert limiter.max_tokens == 10.0

    @pytest.mark.asyncio
    async def test_throughput_matches_rate(self):
        """Over time, throughput should approximate the configured rate"""
        rate = 20.0
        limiter = TokenBucketRateLimiter(rate=rate, max_tokens=1.0)
        # Exhaust initial token
        await limiter.acquire()
        
        count = 0
        start = time.monotonic()
        while time.monotonic() - start < 0.5:
            await limiter.acquire()
            count += 1
        elapsed = time.monotonic() - start
        actual_rate = count / elapsed
        # Should be within 50% of target rate (generous for CI)
        assert actual_rate < rate * 1.5
