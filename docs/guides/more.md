# Credits & concerts

Two more surfaces for richer pages: a track's **credits** (who made it) and an
artist's upcoming **concerts**.

## Track credits

`get_credits(track)` returns a [`Credits`](../reference/models.md#credits) — the
performers, writers, and producers behind a track, each grouped by role and
carrying their sub-roles. It is **cookie-authenticated** (build with an `sp_dc`
cookie — see [authenticated sessions](authentication.md)).

```python
from spotify_scraper import SpotifyClient

with SpotifyClient(cookies="<sp_dc>") as client:
    credits = client.get_credits("4LfCY65LvojKjWEnU7fNN4")
    print(credits.track_title)
    for role in credits.roles:               # "Performers", "Writers", "Producers", …
        people = ", ".join(a.name for a in role.artists)
        print(f"{role.title}: {people}")
```

Each `CreditArtist` carries `name`, `uri`, `image_url`, and `subroles`.

## Artist concerts

`get_artist_events(artist)` returns an artist's upcoming live events as
[`Concert`](../reference/models.md#concert) objects. **Anonymous.** The set can
vary by the request's region, and an artist with no upcoming shows simply returns
an empty tuple.

```python
with SpotifyClient() as client:
    for concert in client.get_artist_events("0gxyHStUsqpMadRV0Di1Qt"):
        print(concert.start_date, concert.title, "—", concert.city)
```

| Field | Type | Notes |
|---|---|---|
| `id` / `uri` | `str` | `spotify:concert:<id>` |
| `title` | `str` | Event title |
| `start_date` | `str \| None` | Raw ISO-8601 start time |
| `city` | `str \| None` | Host city |
| `artists` | `tuple[ArtistRef, ...]` | The line-up |

## Async

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient(cookies="<sp_dc>") as client:
    credits = await client.get_credits("4LfCY65LvojKjWEnU7fNN4")
    events = await client.get_artist_events("0gxyHStUsqpMadRV0Di1Qt")
```
