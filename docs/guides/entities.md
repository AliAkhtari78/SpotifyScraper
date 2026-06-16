# Entities

SpotifyClient exposes one method per entity type. Each returns a **frozen,
typed dataclass** with a JSON-safe `to_dict()`. This guide shows every method
and the fields you get back.

All examples use `SpotifyClient`; the [async client](async.md) has the same
methods with `await`.

## Two extraction tiers (why some fields are `None`)

SpotifyScraper fetches data through a two-tier ladder:

1. **Tier 1** — an anonymous token drives Spotify's GraphQL endpoint, returning
   the rich payload (play counts, follower totals, share URLs, full track
   listings).
2. **Tier 2** — if tier 1's payload changes shape, the library falls back to the
   entity's own embed page, which carries a smaller field set.

Models are designed so that **tier-1-only fields are typed `| None`** and default
to `None` (or empty tuples). When tier 1 succeeds you get everything; when it
degrades to tier 2 you still get a usable object, just with the richer fields
unset. Always guard tier-1 fields:

```python
if artist.monthly_listeners is not None:
    print(f"{artist.monthly_listeners:,} monthly listeners")
```

A degradation is logged at `WARNING` on the `spotify_scraper` logger.

---

## Tracks

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")

print(track.name)                 # "Never Gonna Give You Up"
print(track.artists[0].name)      # "Rick Astley"
print(track.duration_ms)          # 213560
print(track.url)                  # canonical open.spotify.com URL
```

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | 22-char base62 ID. |
| `uri` | `str` | `spotify:track:…` |
| `name` | `str` | |
| `duration_ms` | `int` | Length in milliseconds. |
| `explicit` | `bool` | |
| `playable` | `bool` | |
| `preview_url` | `str \| None` | ~30s MP3 clip URL, when one exists. |
| `artists` | `tuple[ArtistRef, ...]` | Each has `name`, and `uri`/`id` when tier 1. |
| `images` | `tuple[Image, ...]` | Cover art (may be the album's). |
| `release_date` | `datetime \| None` | |
| `album` | `AlbumRef \| None` | **Tier 1 only.** |
| `track_number` | `int \| None` | **Tier 1 only.** |
| `play_count` | `int \| None` | **Tier 1 only.** |
| `share_url` | `str \| None` | **Tier 1 only.** |

The `url` property is always available — it is derived from `id`, not fetched.

---

## Albums

`get_album` paginates the full track list in for you (50 per page).

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    album = client.get_album("6N9PS4QXF1D0OWPk0Sxtb4")

print(album.name)                 # album title
print(album.album_type)           # "album", "single", or "compilation"
print(album.total_tracks)         # e.g. 18
for track in album.tracks:
    print(track.track_number, track.name)
```

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | |
| `uri` | `str` | |
| `name` | `str` | |
| `album_type` | `str` | Lowercased: `"album"`, `"single"`, `"compilation"`. |
| `images` | `tuple[Image, ...]` | |
| `release_date` | `datetime \| None` | |
| `artists` | `tuple[ArtistRef, ...]` | |
| `label` | `str \| None` | **Tier 1 only.** |
| `total_tracks` | `int \| None` | **Tier 1 only.** |
| `tracks` | `tuple[Track, ...]` | All tracks when tier 1 succeeds; empty on tier-2 fallback. |
| `copyrights` | `tuple[str, ...]` | **Tier 1 only.** |
| `share_url` | `str \| None` | **Tier 1 only.** |

---

## Artists

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    artist = client.get_artist("0gxyHStUsqpMadRV0Di1Qt")

print(artist.name)
if artist.monthly_listeners is not None:
    print(f"{artist.monthly_listeners:,} monthly listeners")
for track in artist.top_tracks:
    print("Top:", track.name)
```

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | |
| `uri` | `str` | |
| `name` | `str` | |
| `images` | `tuple[Image, ...]` | |
| `biography` | `str \| None` | **Tier 1 only.** |
| `followers` | `int \| None` | **Tier 1 only.** |
| `monthly_listeners` | `int \| None` | **Tier 1 only.** |
| `world_rank` | `int \| None` | **Tier 1 only.** |
| `top_tracks` | `tuple[Track, ...]` | Empty on tier-2 fallback. |
| `albums` | `tuple[AlbumRef, ...]` | Empty on tier-2 fallback. |
| `singles` | `tuple[AlbumRef, ...]` | Empty on tier-2 fallback. |
| `external_links` | `tuple[str, ...]` | Social/external URLs. |
| `share_url` | `str \| None` | **Tier 1 only.** |

---

## Playlists

`get_playlist` accepts `max_tracks` (default `100`) to bound how many tracks it
collects. Pass `max_tracks=None` to fetch the whole playlist.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    # First 50 tracks
    playlist = client.get_playlist(
        "37i9dQZF1DXcBWIGoYBM5M", max_tracks=50
    )

print(playlist.name)
print(playlist.total_tracks, "tracks in total")
print(len(playlist.tracks), "tracks loaded")

for entry in playlist.tracks:
    print(entry.track.name)              # entry is a PlaylistTrack
    if entry.added_by is not None:
        print("  added by", entry.added_by.name)
```

!!! warning "Playlist entries are wrapped"
    `playlist.tracks` is a tuple of **`PlaylistTrack`**, not `Track`. The actual
    track is `entry.track`; the wrapper adds `added_at` and `added_by`.

**`Playlist`**

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | |
| `uri` | `str` | |
| `name` | `str` | |
| `description` | `str` | Defaults to `""`. |
| `owner` | `UserRef \| None` | |
| `followers` | `int \| None` | **Tier 1 only.** |
| `images` | `tuple[Image, ...]` | |
| `total_tracks` | `int \| None` | **Tier 1 only.** |
| `tracks` | `tuple[PlaylistTrack, ...]` | Up to `max_tracks`. |
| `share_url` | `str \| None` | **Tier 1 only.** |

**`PlaylistTrack`**

| Field | Type | Notes |
|---|---|---|
| `track` | `Track` | The wrapped track. |
| `added_at` | `datetime \| None` | When it was added. |
| `added_by` | `UserRef \| None` | Who added it. |

---

## Episodes

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    episode = client.get_episode("07gKzPFkbvGF0cHoeG7ARS")

print(episode.name)
print(episode.duration_ms / 60000, "minutes")
if episode.show is not None:
    print("From show:", episode.show.name)
```

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | |
| `uri` | `str` | |
| `name` | `str` | |
| `duration_ms` | `int` | |
| `description` | `str` | Defaults to `""`. |
| `explicit` | `bool` | |
| `playable` | `bool` | |
| `release_date` | `datetime \| None` | |
| `images` | `tuple[Image, ...]` | |
| `preview_url` | `str \| None` | Preview clip, when available. |
| `show` | `ShowRef \| None` | **Tier 1 only.** |
| `share_url` | `str \| None` | **Tier 1 only.** |

---

## Shows

`get_show` accepts `max_episodes` (default `50`). Pass `max_episodes=None` to
list every episode.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    show = client.get_show("4rOoJ6Egrf8K2IrywzwOMk", max_episodes=10)

print(show.name)
print(show.publisher)
print(show.total_episodes, "episodes in total")
for episode in show.episodes:           # episodes is a tuple[Episode, ...]
    print(episode.name)
```

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | |
| `uri` | `str` | |
| `name` | `str` | |
| `description` | `str` | Defaults to `""`. |
| `publisher` | `str \| None` | **Tier 1 only.** |
| `media_type` | `str \| None` | **Tier 1 only.** |
| `images` | `tuple[Image, ...]` | |
| `total_episodes` | `int \| None` | **Tier 1 only.** |
| `episodes` | `tuple[Episode, ...]` | Up to `max_episodes`. |
| `topics` | `tuple[str, ...]` | |
| `rating` | `float \| None` | **Tier 1 only.** |
| `share_url` | `str \| None` | **Tier 1 only.** |

---

## Shared value objects

These small references appear inside the entity models.

**`Image`** — `url: str`, `width: int | None`, `height: int | None`.

**`ArtistRef`** — `name: str`, `uri: str` (may be empty on embed data),
`id: str` (may be empty on embed data).

**`AlbumRef`** — `id`, `uri`, `name`, `images: tuple[Image, ...]`.

**`ShowRef`** — `id`, `uri`, `name`, `publisher: str | None`,
`images: tuple[Image, ...]`.

**`UserRef`** — `name: str`, `uri: str` (may be empty).

## Serializing

Every model and value object inherits `to_dict()`:

```python
import json

with SpotifyClient() as client:
    album = client.get_album("6N9PS4QXF1D0OWPk0Sxtb4")

payload = json.dumps(album.to_dict())
```

Round-tripping is supported too — `Album.from_dict(album.to_dict())` rebuilds an
equal model.
