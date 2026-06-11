"""Tests for Spotify URL/URI/ID parsing and construction."""

from __future__ import annotations

import pytest

from spotify_scraper.errors import URLError
from spotify_scraper.urls import ENTITY_TYPES, EntityType, embed_url, entity_uri, entity_url, parse

TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
ALBUM_ID = "4aawyAB9vmqN3uQ7FjRGTy"
ARTIST_ID = "0gxyHStUsqpMadRV0Di1Qt"
PLAYLIST_ID = "37i9dQZF1DXcBWIGoYBM5M"
EPISODE_ID = "07gKzPFkbvGF0cHoeG7ARS"
SHOW_ID = "4rOoJ6Egrf8K2IrywzwOMk"

IDS: dict[str, str] = {
    "track": TRACK_ID,
    "album": ALBUM_ID,
    "artist": ARTIST_ID,
    "playlist": PLAYLIST_ID,
    "episode": EPISODE_ID,
    "show": SHOW_ID,
}

ACCEPTED: tuple[tuple[str, str, str], ...] = (
    *(
        (f"https://open.spotify.com/{entity_type}/{entity_id}", entity_type, entity_id)
        for entity_type, entity_id in IDS.items()
    ),
    *(
        (f"spotify:{entity_type}:{entity_id}", entity_type, entity_id)
        for entity_type, entity_id in IDS.items()
    ),
    *(
        (f"https://open.spotify.com/embed/{entity_type}/{entity_id}", entity_type, entity_id)
        for entity_type, entity_id in IDS.items()
    ),
    (f"http://open.spotify.com/track/{TRACK_ID}", "track", TRACK_ID),
    (f"open.spotify.com/track/{TRACK_ID}", "track", TRACK_ID),
    (f"open.spotify.com/embed/track/{TRACK_ID}", "track", TRACK_ID),
    (f"https://open.spotify.com/track/{TRACK_ID}/", "track", TRACK_ID),
    (f"https://open.spotify.com/track/{TRACK_ID}?si=abc123", "track", TRACK_ID),
    (f"https://open.spotify.com/track/{TRACK_ID}#fragment", "track", TRACK_ID),
    (f"https://open.spotify.com/track/{TRACK_ID}?si=abc&utm_source=x#frag", "track", TRACK_ID),
    (f"https://open.spotify.com/intl-de/track/{TRACK_ID}?si=abc", "track", TRACK_ID),
    (f"https://open.spotify.com/intl-pt-br/album/{ALBUM_ID}", "album", ALBUM_ID),
    (f"open.spotify.com/intl-fr/playlist/{PLAYLIST_ID}", "playlist", PLAYLIST_ID),
    (f"https://open.spotify.com/embed/intl-de/track/{TRACK_ID}", "track", TRACK_ID),
    (f"https://play.spotify.com/track/{TRACK_ID}", "track", TRACK_ID),
    (f"play.spotify.com/show/{SHOW_ID}", "show", SHOW_ID),
    (f"HTTPS://OPEN.SPOTIFY.COM/track/{TRACK_ID}", "track", TRACK_ID),
    (f"  https://open.spotify.com/track/{TRACK_ID}  ", "track", TRACK_ID),
)


@pytest.mark.parametrize(("value", "expected_type", "expected_id"), ACCEPTED)
def test_parse_accepted_forms(value: str, expected_type: str, expected_id: str) -> None:
    assert parse(value) == (expected_type, expected_id)


@pytest.mark.parametrize(("entity_type", "entity_id"), sorted(IDS.items()))
def test_parse_bare_id_with_hint(entity_type: EntityType, entity_id: str) -> None:
    assert parse(entity_id, type_hint=entity_type) == (entity_type, entity_id)


def test_parse_bare_id_without_hint_rejected() -> None:
    with pytest.raises(URLError, match=TRACK_ID):
        parse(TRACK_ID)


def test_parse_url_ignores_type_hint() -> None:
    assert parse(f"https://open.spotify.com/album/{ALBUM_ID}", type_hint="track") == (
        "album",
        ALBUM_ID,
    )


REJECTED: tuple[str, ...] = (
    "",
    "   ",
    "garbage",
    "not a url at all",
    f"https://example.com/track/{TRACK_ID}",
    f"https://music.youtube.com/watch?v={TRACK_ID}",
    f"ftp://open.spotify.com/track/{TRACK_ID}",
    "https://open.spotify.com",
    "https://open.spotify.com/",
    "https://open.spotify.com/track",
    "https://open.spotify.com/track/",
    f"https://open.spotify.com/track/{TRACK_ID}/extra",
    f"https://open.spotify.com/track/{TRACK_ID[:21]}",
    f"https://open.spotify.com/track/{TRACK_ID}x",
    "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQ!",
    "spotify:track",
    f"spotify:track:{TRACK_ID}:extra",
    f"spotify:track:{TRACK_ID[:21]}",
    TRACK_ID[:21],
    f"{TRACK_ID}x",
)


@pytest.mark.parametrize("value", REJECTED)
def test_parse_rejected_inputs(value: str) -> None:
    with pytest.raises(URLError):
        parse(value)


def test_parse_short_bare_id_with_hint_rejected() -> None:
    with pytest.raises(URLError):
        parse(TRACK_ID[:21], type_hint="track")


@pytest.mark.parametrize(
    "value",
    [
        "https://open.spotify.com/concert/abc123",
        f"https://open.spotify.com/concert/{TRACK_ID}",
        f"spotify:concert:{TRACK_ID}",
    ],
)
def test_parse_unsupported_entity_type_named(value: str) -> None:
    with pytest.raises(URLError, match="concert"):
        parse(value)


def test_parse_user_entity_rejected() -> None:
    with pytest.raises(URLError, match="user"):
        parse("https://open.spotify.com/user/spotifycharts")


def test_parse_garbage_message_names_input() -> None:
    with pytest.raises(URLError, match="garbage-input"):
        parse("garbage-input")


def test_entity_types_frozenset() -> None:
    assert frozenset({"track", "album", "artist", "playlist", "episode", "show"}) == ENTITY_TYPES


@pytest.mark.parametrize(("entity_type", "entity_id"), sorted(IDS.items()))
def test_url_construction_round_trips(entity_type: EntityType, entity_id: str) -> None:
    assert (
        entity_url(entity_type, entity_id) == f"https://open.spotify.com/{entity_type}/{entity_id}"
    )
    assert embed_url(entity_type, entity_id) == (
        f"https://open.spotify.com/embed/{entity_type}/{entity_id}"
    )
    assert entity_uri(entity_type, entity_id) == f"spotify:{entity_type}:{entity_id}"
    assert parse(entity_url(entity_type, entity_id)) == (entity_type, entity_id)
    assert parse(embed_url(entity_type, entity_id)) == (entity_type, entity_id)
    assert parse(entity_uri(entity_type, entity_id)) == (entity_type, entity_id)


def test_embed_url_for_token_bootstrap() -> None:
    assert embed_url("track", TRACK_ID) == f"https://open.spotify.com/embed/track/{TRACK_ID}"
