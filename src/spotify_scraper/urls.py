"""Parsing and construction of Spotify URLs, URIs, and entity IDs.

Pure, I/O-free helpers that classify any user-supplied Spotify reference
(URL, embed URL, URI, or bare ID) and build canonical forms from an entity
type and ID.
"""

from __future__ import annotations

import re
from typing import Literal, cast
from urllib.parse import urlsplit

from spotify_scraper.errors import URLError

EntityType = Literal["track", "album", "artist", "playlist", "episode", "show"]

ENTITY_TYPES: frozenset[str] = frozenset(
    {"track", "album", "artist", "playlist", "episode", "show"}
)

_HOSTS = frozenset({"open.spotify.com", "play.spotify.com"})
_ID_RE = re.compile(r"[0-9A-Za-z]{22}")
_INTL_RE = re.compile(r"intl-[A-Za-z]+(?:-[A-Za-z]+)?")
_MARKET_RE = re.compile(r"[A-Za-z]{2}")
_LOCALE_RE = re.compile(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})+")


def parse(value: str, *, type_hint: EntityType | None = None) -> tuple[EntityType, str]:
    """Classify a Spotify URL, URI, or bare ID.

    Args:
        value: A Spotify URL (with or without scheme, with optional
            ``intl-<lang>`` segment and ``/embed`` prefix), a ``spotify:``
            URI, or a bare 22-character base62 ID.
        type_hint: Entity type to assume for bare IDs; required for them.

    Returns:
        The ``(entity_type, entity_id)`` pair.

    Raises:
        URLError: If the input is not a recognizable Spotify reference, the
            entity type is unsupported, or a bare ID lacks ``type_hint``.
    """
    text = value.strip()
    if not text:
        raise URLError(f"Empty Spotify input: {value!r}")
    if _ID_RE.fullmatch(text):
        if type_hint is None:
            raise URLError(f"Bare ID {text!r} requires an explicit type_hint")
        return _checked_type(type_hint, text), text
    if text.startswith("spotify:"):
        return _parse_uri(text)
    return _parse_url(text)


def normalize_locale(value: str) -> str:
    """Validate and normalize a locale for the ``Accept-Language`` header.

    Accepts either a bare ISO-3166 alpha-2 country code (case-insensitive,
    returned upper-cased, e.g. ``"de"`` -> ``"DE"``) or a full language-region
    tag (returned unchanged, e.g. ``"ja-JP"``, ``"en-US"``).

    This sets the *display language* of localized names only; on the anonymous
    ladder it does NOT filter regional availability or vary preview URLs (the
    pathfinder ``market`` variable is inert and the token's country is
    IP-bound). True market/availability requires the authenticated Web API.

    Args:
        value: A country code or language tag.

    Returns:
        The normalized locale string.

    Raises:
        URLError: If ``value`` is neither a valid alpha-2 code nor a valid
            language-region tag.
    """
    text = value.strip()
    if _MARKET_RE.fullmatch(text):
        return text.upper()
    if _LOCALE_RE.fullmatch(text):
        return text
    raise URLError(
        f"Invalid locale {value!r}: expected an ISO-3166 alpha-2 code "
        "(e.g. 'US') or a language tag (e.g. 'ja-JP')."
    )


def entity_url(entity_type: EntityType, entity_id: str) -> str:
    """Return the canonical URL ``https://open.spotify.com/<type>/<id>``."""
    return f"https://open.spotify.com/{entity_type}/{entity_id}"


def embed_url(entity_type: EntityType, entity_id: str) -> str:
    """Return the embed URL ``https://open.spotify.com/embed/<type>/<id>``."""
    return f"https://open.spotify.com/embed/{entity_type}/{entity_id}"


def entity_uri(entity_type: EntityType, entity_id: str) -> str:
    """Return the Spotify URI ``spotify:<type>:<id>``."""
    return f"spotify:{entity_type}:{entity_id}"


def _checked_type(entity_type: str, source: str) -> EntityType:
    if entity_type not in ENTITY_TYPES:
        raise URLError(f"Unsupported Spotify entity type {entity_type!r} in {source!r}")
    return cast(EntityType, entity_type)


def _checked_id(entity_id: str, source: str) -> str:
    if not _ID_RE.fullmatch(entity_id):
        raise URLError(f"Invalid Spotify ID {entity_id!r} in {source!r}")
    return entity_id


def _parse_uri(value: str) -> tuple[EntityType, str]:
    parts = value.split(":")
    if len(parts) != 3:
        raise URLError(f"Unrecognized Spotify URI: {value!r}")
    _, entity_type, entity_id = parts
    return _checked_type(entity_type, value), _checked_id(entity_id, value)


def _parse_url(value: str) -> tuple[EntityType, str]:
    candidate = value if "://" in value else f"https://{value}"
    split = urlsplit(candidate)
    if split.scheme not in {"http", "https"} or split.hostname not in _HOSTS:
        raise URLError(f"Not a Spotify URL: {value!r}")
    segments = [segment for segment in split.path.split("/") if segment]
    if segments and segments[0] == "embed":
        del segments[0]
    if segments and _INTL_RE.fullmatch(segments[0]):
        del segments[0]
    if len(segments) != 2:
        raise URLError(f"Unrecognized Spotify URL path: {value!r}")
    entity_type, entity_id = segments
    return _checked_type(entity_type, value), _checked_id(entity_id, value)
