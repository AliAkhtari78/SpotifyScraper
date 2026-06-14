"""Live smoke tests for ``locale`` display-language localization (no cookie).

Proves the ``Accept-Language`` lever works end to end: a Japanese locale yields
a transliterated (non-ASCII) artist display name that differs from the default
English one. A negative-scope guard documents the honest limitation — ``locale``
localizes display-name LANGUAGE only; it does NOT change availability/playability
(true regional availability/market is not achievable anonymously).
"""

from __future__ import annotations

import pytest

from spotify_scraper import SpotifyClient

# "Never Gonna Give You Up" — Rick Astley transliterates to リック・アストリー under ja.
NEVER_GONNA = "4uLU6hMCjMI75M1A2tKUQC"


def _is_ascii(text: str) -> bool:
    return text.isascii()


@pytest.mark.live
def test_locale_localizes_artist_name() -> None:
    with SpotifyClient() as client:  # no cookie
        default_track = client.get_track(NEVER_GONNA)
        ja_track = client.get_track(NEVER_GONNA, locale="ja")

    default_name = default_track.artists[0].name
    ja_name = ja_track.artists[0].name

    assert ja_name != default_name
    assert _is_ascii(default_name)
    assert not _is_ascii(ja_name)


@pytest.mark.live
def test_locale_does_not_change_availability() -> None:
    # Negative-scope guard: locale is a language lever, not a market lever.
    with SpotifyClient() as client:
        en_track = client.get_track(NEVER_GONNA, locale="en")
        ja_track = client.get_track(NEVER_GONNA, locale="ja")

    assert en_track.explicit == ja_track.explicit
    assert en_track.playable == ja_track.playable
    assert en_track.duration_ms == ja_track.duration_ms
    assert (en_track.preview_url is None) == (ja_track.preview_url is None)
