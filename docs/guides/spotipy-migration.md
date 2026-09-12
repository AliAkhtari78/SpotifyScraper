# Migrating from spotipy

Spotify deprecated a batch of Web API endpoints in **November 2024**. Apps
created after the announcement get an error instead of data, so a lot of
spotipy code that used to work now fails. The affected calls include
`sp.recommendations()`, `sp.artist_related_artists()`, `sp.audio_features()`,
and `sp.audio_analysis()`.

SpotifyScraper reads the same public pages the Spotify web player reads, so the
**discovery** parts have a direct replacement and need no API key, no client
secret, and no OAuth dance. The audio-analysis parts do not — see
[what cannot be restored](#what-cannot-be-restored).

## Related artists

=== "Before — spotipy"

    ```python
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    related = sp.artist_related_artists("0gxyHStUsqpMadRV0Di1Qt")

    for artist in related["artists"]:
        print(artist["name"])
    ```

    Deprecated. New client credentials get an error response rather than the
    artist list.

=== "After — SpotifyScraper"

    ```python
    from spotify_scraper import SpotifyClient

    with SpotifyClient() as client:
        for artist in client.get_related_artists("0gxyHStUsqpMadRV0Di1Qt"):
            print(artist.name)
    ```

    Anonymous — no credentials at all. Returns a tuple of typed
    [`Artist`](../reference/models.md#artist) objects with images, so you get
    `artist.name` instead of `artist["name"]`.

## Recommendations

`sp.recommendations()` took seed tracks/artists/genres and tunable attributes.
There is no public page behind that, so the replacement is not identical: what
Spotify still exposes publicly is *"fans of this track also like"*, keyed off a
single track.

=== "Before — spotipy"

    ```python
    recs = sp.recommendations(seed_tracks=["4uLU6hMCjMI75M1A2tKUQC"], limit=10)

    for track in recs["tracks"]:
        print(track["name"])
    ```

    Deprecated, and the `target_energy` / `min_danceability` style tuning
    parameters have no equivalent anywhere.

=== "After — SpotifyScraper"

    ```python
    from spotify_scraper import SpotifyClient

    with SpotifyClient() as client:
        for album in client.get_similar_albums("4uLU6hMCjMI75M1A2tKUQC", limit=10):
            print(album.name)
    ```

    Anonymous. Note the shape difference: you get **albums**, not tracks, from
    one seed track. Combine it with
    [`get_discography()`](discovery.md#full-discography) if you need the
    individual releases behind an artist.

Both methods are documented in full under [Discovery](discovery.md), and both
mirror on the async client:

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient() as client:
    related = await client.get_related_artists("0gxyHStUsqpMadRV0Di1Qt")
    albums = await client.get_similar_albums("4uLU6hMCjMI75M1A2tKUQC", limit=5)
```

Or straight from the shell, without writing any Python:

```bash
spotifyscraper related 0gxyHStUsqpMadRV0Di1Qt --pretty
```

## What cannot be restored

!!! warning "No replacement for audio features"

    `sp.audio_features()` and `sp.audio_analysis()` returned `danceability`,
    `energy`, `valence`, `tempo`, `key`, and friends. Spotify removed those
    endpoints and does **not** expose the values on any public page, so
    SpotifyScraper cannot bring them back. If your code ranks or filters tracks
    by audio features, that logic needs to be redesigned around data you can
    still get — or moved to a different source, such as your own audio analysis
    of files you already own.

The same applies to the tuning knobs on `recommendations()`: they were computed
from those audio features, so they went away with them.

## Quick reference

| spotipy call | Status | SpotifyScraper |
|---|---|---|
| `sp.artist_related_artists(id)` | Deprecated | `client.get_related_artists(id)` |
| `sp.recommendations(seed_tracks=[id])` | Deprecated | `client.get_similar_albums(id)` — albums, not tracks |
| `sp.artist_albums(id)` | Works | `client.get_discography(id)` — no key needed |
| `sp.audio_features(ids)` | Deprecated | **No equivalent** |
| `sp.audio_analysis(id)` | Deprecated | **No equivalent** |

For everything else — tracks, albums, artists, playlists, podcasts, lyrics —
start at [Entities](entities.md).
