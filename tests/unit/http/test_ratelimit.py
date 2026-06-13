"""Tests for token-bucket math and the sync/async bucket wrappers."""

from __future__ import annotations

import pytest

from spotify_scraper.http.ratelimit import AsyncTokenBucket, RateLimit, TokenBucket, consume

CONFIG = RateLimit(per_second=2.0, burst=5)


class FakeClock:
    """Manually advanced monotonic clock whose sleeps move time forward."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds

    async def async_sleep(self, seconds: float) -> None:
        self.sleep(seconds)


def test_defaults() -> None:
    config = RateLimit()
    assert config.per_second == 2.0
    assert config.burst == 5


@pytest.mark.parametrize(
    ("tokens", "last_refill", "now", "expected"),
    [
        (5.0, 0.0, 0.0, (4.0, 0.0)),
        (1.0, 0.0, 0.0, (0.0, 0.0)),
        (0.0, 0.0, 0.0, (0.0, 0.5)),
        (0.5, 0.0, 0.0, (0.5, 0.25)),
        (0.0, 0.0, 0.5, (0.0, 0.0)),
        (0.0, 0.0, 100.0, (4.0, 0.0)),
        (5.0, 0.0, 100.0, (4.0, 0.0)),
    ],
)
def test_consume_table(
    tokens: float, last_refill: float, now: float, expected: tuple[float, float]
) -> None:
    assert consume(tokens, last_refill, now, CONFIG) == expected


def test_consume_wait_scales_with_rate() -> None:
    slow = RateLimit(per_second=0.5, burst=1)
    assert consume(0.0, 0.0, 0.0, slow) == (0.0, 2.0)


def test_bucket_burst_then_throttle() -> None:
    clock = FakeClock()
    bucket = TokenBucket(RateLimit(per_second=1.0, burst=2), clock=clock, sleep=clock.sleep)

    bucket.acquire()
    bucket.acquire()
    assert clock.sleeps == []

    bucket.acquire()
    assert clock.sleeps == [1.0]
    assert clock.now == 1.0


def test_bucket_refills_while_idle() -> None:
    clock = FakeClock()
    bucket = TokenBucket(RateLimit(per_second=2.0, burst=1), clock=clock, sleep=clock.sleep)

    bucket.acquire()
    clock.now += 10.0
    bucket.acquire()
    assert clock.sleeps == []


def test_bucket_refill_caps_at_burst() -> None:
    clock = FakeClock()
    bucket = TokenBucket(RateLimit(per_second=1.0, burst=2), clock=clock, sleep=clock.sleep)

    clock.now += 1000.0
    bucket.acquire()
    bucket.acquire()
    bucket.acquire()
    assert clock.sleeps == [1.0]


async def test_async_bucket_burst_then_throttle() -> None:
    clock = FakeClock()
    bucket = AsyncTokenBucket(
        RateLimit(per_second=1.0, burst=2), clock=clock, sleep=clock.async_sleep
    )

    await bucket.acquire()
    await bucket.acquire()
    assert clock.sleeps == []

    await bucket.acquire()
    assert clock.sleeps == [1.0]


async def test_async_bucket_refills_while_idle() -> None:
    clock = FakeClock()
    bucket = AsyncTokenBucket(
        RateLimit(per_second=2.0, burst=1), clock=clock, sleep=clock.async_sleep
    )

    await bucket.acquire()
    clock.now += 10.0
    await bucket.acquire()
    assert clock.sleeps == []


@pytest.mark.parametrize("kwargs", [{"per_second": 0}, {"per_second": -1.0}, {"burst": 0}])
def test_ratelimit_rejects_invalid(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        RateLimit(**kwargs)
