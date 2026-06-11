"""Retry policy and pure backoff math for HTTP transports.

The transports decide *whether* to sleep; this module only computes *how
long*, so the logic is fully testable without any clock.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Retry configuration for a transport.

    Attributes:
        max_attempts: Total attempts allowed, including the first request.
        backoff_base: Delay in seconds before the second attempt; doubles on
            each subsequent retry.
        backoff_max: Ceiling in seconds for any single computed delay; a
            ``Retry-After`` hint above this budget aborts retrying.
    """

    max_attempts: int = 4
    backoff_base: float = 0.5
    backoff_max: float = 30.0


def backoff_delay(policy: RetryPolicy, attempt: int, retry_after: float | None) -> float | None:
    """Compute the sleep before the next attempt, or ``None`` to give up.

    Args:
        policy: Active retry policy.
        attempt: 1-based number of the attempt that just failed.
        retry_after: Server-provided ``Retry-After`` hint in seconds, if any.

    Returns:
        Seconds to sleep (exponential backoff with jitter, or the honored
        ``retry_after``), or ``None`` when attempts are exhausted or the hint
        exceeds ``policy.backoff_max``.
    """
    if attempt >= policy.max_attempts:
        return None
    if retry_after is not None:
        if retry_after > policy.backoff_max:
            return None
        delay = retry_after
    else:
        delay = min(policy.backoff_base * 2 ** (attempt - 1), policy.backoff_max)
    return delay + random.uniform(0, 0.25 * delay)  # noqa: S311
