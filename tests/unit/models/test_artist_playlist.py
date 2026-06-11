"""Construction, immutability, and serialization tests for Artist and Playlist."""

from __future__ import annotations

import dataclasses
import json
from datetime import datetime, timezone

import pytest

from spotify_scraper.models.artist import Artist
from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import AlbumRef, ArtistRef, Image, UserRef
from spotify_scraper.models.playlist import Playlist, PlaylistTrack
from spotify_scraper.models.track import Track

ARTIST_ID = "0gxyHStUsqpMadRV0Di1Qt"
PLAYLIST_ID = "37i9dQZF1DXcBWIGoYBM5M"
TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
ALBUM_ID = "6N9PS4QXF1D0OWPk0Sxtb4"

IMAGES = (
    Image(url="https://i.scdn.co/image/ab67616d00001e02", width=300, height=300),
    Image(url="https://i.scdn.co/image/ab67616d00004851", width=64, height=64),
)

ALBUM_REF = AlbumRef(
    id=ALBUM_ID,
    uri=f"spotify:album:{ALBUM_ID}",
    name="Whenever You Need Somebody",
    images=IMAGES,
)

OWNER = UserRef(name="Spotify", uri="spotify:user:spotify")


def make_track() -> Track:
    return Track(
        id=TRACK_ID,
        uri=f"spotify:track:{TRACK_ID}",
        name="Never Gonna Give You Up",
        duration_ms=213573,
        explicit=False,
        playable=True,
        preview_url="https://p.scdn.co/mp3-preview/ab67616d",
        artists=(ArtistRef(name="Rick Astley", uri=f"spotify:artist:{ARTIST_ID}", id=ARTIST_ID),),
        images=IMAGES,
        release_date=datetime(1987, 11, 12, tzinfo=timezone.utc),
        album=ALBUM_REF,
        track_number=1,
        play_count=1137719792,
        share_url=f"https://open.spotify.com/track/{TRACK_ID}?si=share",
    )


def make_full_artist() -> Artist:
    return Artist(
        id=ARTIST_ID,
        uri=f"spotify:artist:{ARTIST_ID}",
        name="Rick Astley",
        images=IMAGES,
        biography="It's one of contemporary music's most unlikely tales.",
        followers=1567830,
        monthly_listeners=7672890,
        world_rank=0,
        top_tracks=(make_track(),),
        albums=(ALBUM_REF,),
        singles=(
            AlbumRef(
                id="0xOvvd9BQwlhJTnKfgB2zz",
                uri="spotify:album:0xOvvd9BQwlhJTnKfgB2zz",
                name="Raindrops",
            ),
        ),
        external_links=("https://www.rickastley.co.uk",),
        share_url=f"https://open.spotify.com/artist/{ARTIST_ID}?si=share",
    )


def make_minimal_artist() -> Artist:
    return Artist(
        id=ARTIST_ID, uri=f"spotify:artist:{ARTIST_ID}", name="Rick Astley", images=IMAGES
    )


def make_full_playlist_track() -> PlaylistTrack:
    return PlaylistTrack(
        track=make_track(),
        added_at=datetime(2026, 5, 29, 4, 2, 20, tzinfo=timezone.utc),
        added_by=OWNER,
    )


def make_full_playlist() -> Playlist:
    return Playlist(
        id=PLAYLIST_ID,
        uri=f"spotify:playlist:{PLAYLIST_ID}",
        name="Today's Top Hits",
        description="The hottest 50. Cover: Ariana Grande",
        owner=OWNER,
        followers=34284032,
        images=IMAGES,
        total_tracks=50,
        tracks=(make_full_playlist_track(),),
        share_url=f"https://open.spotify.com/playlist/{PLAYLIST_ID}?si=share",
    )


def make_minimal_playlist() -> Playlist:
    return Playlist(id=PLAYLIST_ID, uri=f"spotify:playlist:{PLAYLIST_ID}", name="Today's Top Hits")


def _assert_json_primitives(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            assert isinstance(key, str)
            _assert_json_primitives(item)
    elif isinstance(value, list):
        for item in value:
            _assert_json_primitives(item)
    else:
        assert value is None or isinstance(value, (str, int, float, bool))


def test_full_artist_construction() -> None:
    artist = make_full_artist()
    assert artist.id == ARTIST_ID
    assert artist.uri == f"spotify:artist:{ARTIST_ID}"
    assert artist.followers == 1567830
    assert artist.monthly_listeners == 7672890
    assert artist.world_rank == 0
    assert artist.top_tracks[0].name == "Never Gonna Give You Up"
    assert artist.albums[0] is ALBUM_REF
    assert artist.singles[0].name == "Raindrops"


def test_minimal_artist_uses_defaults() -> None:
    artist = make_minimal_artist()
    assert artist.biography is None
    assert artist.followers is None
    assert artist.monthly_listeners is None
    assert artist.world_rank is None
    assert artist.top_tracks == ()
    assert artist.albums == ()
    assert artist.singles == ()
    assert artist.external_links == ()
    assert artist.share_url is None


def test_full_playlist_construction() -> None:
    playlist = make_full_playlist()
    assert playlist.id == PLAYLIST_ID
    assert playlist.description == "The hottest 50. Cover: Ariana Grande"
    assert playlist.owner == OWNER
    assert playlist.followers == 34284032
    assert playlist.total_tracks == 50
    assert playlist.tracks[0].track.id == TRACK_ID
    assert playlist.tracks[0].added_by == OWNER


def test_minimal_playlist_uses_defaults() -> None:
    playlist = make_minimal_playlist()
    assert playlist.description == ""
    assert playlist.owner is None
    assert playlist.followers is None
    assert playlist.images == ()
    assert playlist.total_tracks is None
    assert playlist.tracks == ()
    assert playlist.share_url is None


def test_minimal_playlist_track_uses_defaults() -> None:
    entry = PlaylistTrack(track=make_track())
    assert entry.added_at is None
    assert entry.added_by is None


@pytest.mark.parametrize(
    "instance",
    [make_full_artist(), make_full_playlist(), make_full_playlist_track()],
    ids=lambda m: type(m).__name__,
)
def test_models_are_frozen(instance: ModelBase) -> None:
    field_name = dataclasses.fields(instance)[0].name  # type: ignore[arg-type]
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(instance, field_name, "mutated")


@pytest.mark.parametrize(
    "instance",
    [
        make_full_artist(),
        make_minimal_artist(),
        make_full_playlist(),
        make_minimal_playlist(),
        make_full_playlist_track(),
        PlaylistTrack(track=make_track()),
    ],
    ids=lambda m: type(m).__name__,
)
def test_round_trip_equality(instance: ModelBase) -> None:
    assert type(instance).from_dict(instance.to_dict()) == instance


@pytest.mark.parametrize(
    "instance",
    [make_full_artist(), make_full_playlist(), make_full_playlist_track()],
    ids=lambda m: type(m).__name__,
)
def test_to_dict_is_json_safe(instance: ModelBase) -> None:
    data = instance.to_dict()
    _assert_json_primitives(data)
    json.dumps(data)


def test_round_trip_rebuilds_nested_models() -> None:
    playlist = make_full_playlist()
    rebuilt = Playlist.from_dict(playlist.to_dict())
    assert isinstance(rebuilt.tracks, tuple)
    assert isinstance(rebuilt.tracks[0], PlaylistTrack)
    assert isinstance(rebuilt.tracks[0].track, Track)
    assert rebuilt.tracks[0].added_at == playlist.tracks[0].added_at


def test_url_property_is_derived_and_not_serialized() -> None:
    artist = make_minimal_artist()
    playlist = make_minimal_playlist()
    assert artist.url == f"https://open.spotify.com/artist/{ARTIST_ID}"
    assert playlist.url == f"https://open.spotify.com/playlist/{PLAYLIST_ID}"
    assert "url" not in artist.to_dict()
    assert "url" not in playlist.to_dict()
