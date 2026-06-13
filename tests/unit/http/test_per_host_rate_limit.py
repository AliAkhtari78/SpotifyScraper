"""Per-host rate limiting: resolution rules and independent buckets."""

from __future__ import annotations

import pytest

from spotify_scraper.http.ratelimit import (
    PARTNER_API_HOST,
    RateLimit,
    resolve_rate_limit,
)
from spotify_scraper.http.transport import AsyncHttpxTransport, HttpxTransport

CUSTOM = RateLimit(per_second=9.0, burst=9)


@pytest.mark.parametrize(
    ("host", "default", "overrides", "expected"),
    [
        ("api-partner.spotify.com", None, {}, RateLimit()),
        ("open.spotify.com", None, {}, RateLimit()),
        ("api-partner.spotify.com", CUSTOM, {}, CUSTOM),  # explicit global applies everywhere
        ("open.spotify.com", CUSTOM, {}, CUSTOM),
        (
            "api-partner.spotify.com",
            None,
            {"api-partner.spotify.com": CUSTOM},
            CUSTOM,
        ),  # override wins
        ("api-partner.spotify.com", CUSTOM, {"api-partner.spotify.com": RateLimit()}, RateLimit()),
    ],
)
def test_resolve_rate_limit(
    host: str, default: RateLimit | None, overrides: dict[str, RateLimit], expected: RateLimit
) -> None:
    assert resolve_rate_limit(host, default, overrides) == expected


def test_transport_buckets_are_per_host() -> None:
    transport = HttpxTransport()
    partner = transport._bucket_for(PARTNER_API_HOST)
    embed = transport._bucket_for("open.spotify.com")
    assert partner is not embed  # independent buckets
    assert transport._bucket_for(PARTNER_API_HOST) is partner  # cached, not recreated
    assert partner._config == RateLimit()
    assert embed._config == RateLimit()
    transport.close()


def test_transport_host_override_wins() -> None:
    transport = HttpxTransport(host_rate_limits={PARTNER_API_HOST: CUSTOM})
    assert transport._bucket_for(PARTNER_API_HOST)._config == CUSTOM
    assert transport._bucket_for("open.spotify.com")._config == RateLimit()
    transport.close()


async def test_async_transport_buckets_are_per_host() -> None:
    transport = AsyncHttpxTransport(host_rate_limits={PARTNER_API_HOST: CUSTOM})
    partner = transport._bucket_for(PARTNER_API_HOST)
    embed = transport._bucket_for("open.spotify.com")
    assert partner is not embed
    assert partner._config == CUSTOM
    assert embed._config == RateLimit()
    await transport.aclose()
