"""Live smoke tests for cookie-authenticated account product-state.

Gated on ``SPOTIFY_SP_DC`` and ``@pytest.mark.live`` (excluded by default). The
product-state endpoint is confirmed (2026-06-15, real Premium account) to return
a flat JSON object with a ``product`` of ``premium`` / ``free`` / ``open`` and an
ISO ``country``.
"""

from __future__ import annotations

import os

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

_SP_DC = os.environ.get("SPOTIFY_SP_DC")

pytestmark = pytest.mark.skipif(not _SP_DC, reason="SPOTIFY_SP_DC env var not set")


@pytest.mark.live
def test_get_account_live() -> None:
    with SpotifyClient(cookies=_SP_DC) as client:
        account = client.get_account()
        assert account.product is not None
        assert account.product in {"premium", "free", "open"}
        assert account.country
        assert client.is_premium() == account.is_premium


@pytest.mark.live
async def test_get_account_live_async() -> None:
    async with AsyncSpotifyClient(cookies=_SP_DC) as client:
        account = await client.get_account()
        assert account.product is not None
        assert account.product in {"premium", "free", "open"}
        assert account.country
        assert (await client.is_premium()) == account.is_premium
