# Search

`search()` runs an aggregate Spotify search across every public entity type and
returns one typed [`SearchResults`](../reference/models.md). It is **anonymous**
— the same tier-1 bearer token as the entity getters, no cookie and no embed
page — so it needs no authentication.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    results = client.search("daft punk")
    print(results.total, "track matches")          # tracks' totalCount

    for track in results.tracks:
        print(track.name, "—", track.artists[0].name)
    for artist in results.artists:
        print(artist.name)
    for album in results.albums:                    # lightweight AlbumRef
        print(album.name)
```

## What you get back

`SearchResults` holds one tuple per entity type, reusing the existing models:

| Field | Type | Notes |
|---|---|---|
| `query` | `str` | The term you searched for |
| `tracks` | `tuple[Track, ...]` | Full track hits |
| `artists` | `tuple[Artist, ...]` | Artist hits |
| `albums` | `tuple[AlbumRef, ...]` | Lightweight — no tracklist (search returns none) |
| `playlists` | `tuple[Playlist, ...]` | Playlist hits |
| `shows` | `tuple[ShowRef, ...]` | Lightweight — no episode list |
| `episodes` | `tuple[Episode, ...]` | Episode hits |
| `total` | `int \| None` | Spotify's reported **track** match count |

Search hits are **sparse**: fields that only a full entity fetch supplies stay
`None`/`()`. To get an album's tracklist or a show's episodes, pass the hit's
`id` to `get_album()` / `get_show()`. `total` reflects the *tracks* section only
(the other sections don't report a count); it is `None` when `"track"` is not
among the requested `types`.

## Narrowing the search

Pass `types=` to fetch only the sections you need, and `limit=` for the maximum
hits per section (Spotify caps this):

```python
# Only artists and playlists, up to 5 each:
results = client.search("lo-fi", types=("artist", "playlist"), limit=5)
assert results.tracks == ()                  # not requested -> empty
```

Accepted types are `"track"`, `"album"`, `"artist"`, `"playlist"`, `"show"`, and
`"episode"`. An unrecognized type raises `URLError` before any request. A query
that matches nothing returns an **empty** `SearchResults`, never an error.

## Async

The async client mirrors it:

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient() as client:
    results = await client.search("daft punk", types=("track",), limit=10)
```
