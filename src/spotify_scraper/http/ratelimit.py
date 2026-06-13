"""Client-side request throttling via a token bucket.

The bucket math is a pure function over ``(tokens, last_refill, now)``;
:class:`TokenBucket` and :class:`AsyncTokenBucket` only differ in how they
lock and sleep.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RateLimit:
    """Token-bucket configuration.

    Attributes:
        per_second: Sustained request rate (token refill rate).
        burst: Bucket capacity — how many requests may go out instantly.
    """

    per_second: float = 2.0
    burst: int = 5


#: Spotify's pathfinder GraphQL host. Exposed as a constant so callers can
#: target it in ``host_rate_limits`` if they ever need to throttle it harder
#: (e.g. behind a shared IP). Measured behavior (June 2026): it tolerates dozens
#: of rapid anonymous requests, so the library does not throttle it by default;
#: transient 403s are retried instead.
PARTNER_API_HOST = "api-partner.spotify.com"


def resolve_rate_limit(
    host: str,
    default: RateLimit | None,
    overrides: Mapping[str, RateLimit],
) -> RateLimit:
    """Pick the rate limit for a host.

    An explicit per-host override wins; otherwise the global default (or the
    built-in :class:`RateLimit` when none was supplied) applies.

    Args:
        host: Destination host name.
        default: Caller-supplied global rate, or ``None`` for the built-in.
        overrides: Per-host rate overrides (always win).

    Returns:
        The :class:`RateLimit` to throttle ``host`` with.
    """
    if host in overrides:
        return overrides[host]
    return default or RateLimit()


def consume(
    tokens: float, last_refill: float, now: float, config: RateLimit
) -> tuple[float, float]:
    """Refill the bucket to ``now`` and try to take one token.

    Args:
        tokens: Tokens available at ``last_refill``.
        last_refill: Clock reading of the previous refill.
        now: Current clock reading (same monotonic clock).
        config: Bucket configuration.

    Returns:
        ``(new_tokens, wait_seconds)`` — when ``wait_seconds`` is ``0.0`` a
        token was consumed; otherwise the caller should sleep that long and
        try again with ``new_tokens`` and ``last_refill=now``.
    """
    tokens = min(float(config.burst), tokens + (now - last_refill) * config.per_second)
    if tokens >= 1.0:
        return tokens - 1.0, 0.0
    return tokens, (1.0 - tokens) / config.per_second


class TokenBucket:
    """Thread-safe token bucket that blocks via ``sleep`` until permitted."""

    def __init__(
        self,
        config: RateLimit,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Initialize a full bucket.

        Args:
            config: Bucket configuration.
            clock: Monotonic clock, injectable for tests.
            sleep: Blocking sleep, injectable for tests.
        """
        self._config = config
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()
        self._tokens = float(config.burst)
        self._last_refill = clock()

    def acquire(self) -> None:
        """Block until a token is available, then consume it."""
        while True:
            with self._lock:
                now = self._clock()
                self._tokens, wait = consume(self._tokens, self._last_refill, now, self._config)
                self._last_refill = now
            if wait <= 0.0:
                return
            self._sleep(wait)


class AsyncTokenBucket:
    """Asyncio token bucket that awaits ``sleep`` until permitted."""

    def __init__(
        self,
        config: RateLimit,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        """Initialize a full bucket.

        Args:
            config: Bucket configuration.
            clock: Monotonic clock, injectable for tests.
            sleep: Awaitable sleep, injectable for tests.
        """
        self._config = config
        self._clock = clock
        self._sleep = sleep
        self._lock = asyncio.Lock()
        self._tokens = float(config.burst)
        self._last_refill = clock()

    async def acquire(self) -> None:
        """Wait until a token is available, then consume it."""
        while True:
            async with self._lock:
                now = self._clock()
                self._tokens, wait = consume(self._tokens, self._last_refill, now, self._config)
                self._last_refill = now
            if wait <= 0.0:
                return
            await self._sleep(wait)
