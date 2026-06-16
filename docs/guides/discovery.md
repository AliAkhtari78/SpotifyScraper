# Discovery

Beyond fetching a known entity, SpotifyScraper surfaces Spotify's discovery
graph: artists related to an artist, an artist's full discography, album
recommendations from a track, and public user profiles.

## Related artists

`get_related_artists(artist)` returns Spotify's "fans also like" — a tuple of
[`Artist`](../reference/models.md#artist) (with images). **Anonymous.**

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    for artist in client.get_related_artists("0gxyHStUsqpMadRV0Di1Qt"):
        print(artist.name)
```

## Full discography

`get_discography(artist, max_releases=None)` paginates **every** release — albums,
singles, and compilations — and returns them as
[`AlbumRef`](../reference/models.md#albumref) objects in Spotify's discography
order. **Anonymous.** Pass `max_releases` to cap the count.

```python
releases = client.get_discography("0gxyHStUsqpMadRV0Di1Qt", max_releases=50)
print(len(releases), "releases")
```

## Recommendations

`get_similar_albums(track, limit=10)` recommends albums similar to a track
(Spotify's "fans of this track also like"). **Anonymous.**

```python
for album in client.get_similar_albums("4uLU6hMCjMI75M1A2tKUQC", limit=10):
    print(album.name)
```

## Public user profiles

`get_user(user_id)` returns a public
[`UserProfile`](../reference/models.md#userprofile) — name, follower/following
counts, public playlists, and recently-played artists. It is
**cookie-authenticated** (Spotify refuses the anonymous token for profiles with
`403`), so build the client with an `sp_dc` cookie — see
[authenticated sessions](authentication.md).

```python
with SpotifyClient(cookies="<sp_dc>") as client:
    profile = client.get_user("spotify")      # id, spotify:user:<id> uri, or profile URL
    print(profile.name, profile.followers_count)
    for playlist in profile.public_playlists:
        print(playlist.name)
```

| Field | Type | Notes |
|---|---|---|
| `id` / `uri` / `name` | `str` | Identity |
| `images` | `tuple[Image, ...]` | Avatar |
| `followers_count` / `following_count` | `int \| None` | Public counts |
| `public_playlists` | `tuple[Playlist, ...]` | Lightweight playlist refs |
| `public_playlists_total` | `int \| None` | Total public playlists |
| `recently_played_artists` | `tuple[ArtistRef, ...]` | Populated for some accounts |
| `is_verified` | `bool \| None` | Verified profile flag |

## Async

Every method mirrors on the async client:

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient(cookies="<sp_dc>") as client:
    related = await client.get_related_artists("0gxyHStUsqpMadRV0Di1Qt")
    profile = await client.get_user("spotify")
```
