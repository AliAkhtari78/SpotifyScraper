"""Sync/async client API parity."""

from __future__ import annotations

import inspect

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

_LIFECYCLE = {"close", "aclose"}


def _public_members(cls: type) -> set[str]:
    return {
        name
        for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction)
        if not name.startswith("_")
    }


def test_public_method_sets_match_modulo_lifecycle() -> None:
    sync_members = _public_members(SpotifyClient) - _LIFECYCLE
    async_members = _public_members(AsyncSpotifyClient) - _LIFECYCLE
    assert sync_members == async_members


def test_data_methods_share_signatures() -> None:
    sync_members = _public_members(SpotifyClient) - _LIFECYCLE
    for name in sync_members:
        sync_sig = inspect.signature(getattr(SpotifyClient, name))
        async_sig = inspect.signature(getattr(AsyncSpotifyClient, name))
        assert list(sync_sig.parameters) == list(async_sig.parameters)
        assert sync_sig.return_annotation == async_sig.return_annotation


def test_lifecycle_methods_present() -> None:
    assert hasattr(SpotifyClient, "close")
    assert hasattr(AsyncSpotifyClient, "aclose")
    assert inspect.iscoroutinefunction(AsyncSpotifyClient.get_track)
    assert not inspect.iscoroutinefunction(SpotifyClient.get_track)
