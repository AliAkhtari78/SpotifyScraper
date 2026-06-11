"""Tests for the pure backoff math in spotify_scraper.http.retry."""

from __future__ import annotations

import pytest

from spotify_scraper.http.retry import RetryPolicy, backoff_delay

POLICY = RetryPolicy(max_attempts=4, backoff_base=0.5, backoff_max=30.0)


def test_defaults() -> None:
    policy = RetryPolicy()
    assert policy.max_attempts == 4
    assert policy.backoff_base == 0.5
    assert policy.backoff_max == 30.0


@pytest.mark.parametrize(
    ("attempt", "base_delay"),
    [(1, 0.5), (2, 1.0), (3, 2.0)],
)
def test_exponential_growth_with_jitter_bounds(attempt: int, base_delay: float) -> None:
    delay = backoff_delay(POLICY, attempt, None)
    assert delay is not None
    assert base_delay <= delay <= base_delay * 1.25


@pytest.mark.parametrize("attempt", [4, 5, 100])
def test_gives_up_at_max_attempts(attempt: int) -> None:
    assert backoff_delay(POLICY, attempt, None) is None


def test_delay_capped_at_backoff_max() -> None:
    policy = RetryPolicy(max_attempts=50, backoff_base=0.5, backoff_max=30.0)
    delay = backoff_delay(policy, 20, None)
    assert delay is not None
    assert 30.0 <= delay <= 30.0 * 1.25


@pytest.mark.parametrize("retry_after", [0.0, 1.0, 30.0])
def test_retry_after_honored_within_budget(retry_after: float) -> None:
    delay = backoff_delay(POLICY, 1, retry_after)
    assert delay is not None
    assert retry_after <= delay <= retry_after * 1.25


def test_retry_after_beyond_budget_gives_up_even_on_first_attempt() -> None:
    assert backoff_delay(POLICY, 1, 47231.0) is None
    assert backoff_delay(POLICY, 1, 30.001) is None


def test_retry_after_ignored_once_attempts_exhausted() -> None:
    assert backoff_delay(POLICY, 4, 1.0) is None


def test_zero_backoff_base_yields_zero_delay() -> None:
    policy = RetryPolicy(max_attempts=4, backoff_base=0.0)
    for attempt in (1, 2, 3):
        assert backoff_delay(policy, attempt, None) == 0.0


def test_policy_is_frozen() -> None:
    with pytest.raises(AttributeError):
        POLICY.max_attempts = 9  # type: ignore[misc]
