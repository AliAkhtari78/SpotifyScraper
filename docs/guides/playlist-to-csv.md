# Playlist → CSV

A common ask: dump a playlist's tracks to a spreadsheet. This fetches a
playlist and writes `name, artist, album, duration_ms` rows with nothing but
the public API and the standard library's `csv` module.

```python
import csv

from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    playlist = client.get_playlist("37i9dQZF1DXcBWIGoYBM5M", max_tracks=None)

with open("playlist.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "artist", "album", "duration_ms"])
    for entry in playlist.tracks:
        track = entry.track
        artist = ", ".join(a.name for a in track.artists)
        album = track.album.name if track.album is not None else ""
        writer.writerow([track.name, artist, album, track.duration_ms])
```

`playlist.tracks` holds [`PlaylistTrack`](../reference/models.md#playlisttrack)
entries, not `Track` directly — see [entities](entities.md#playlists) for why.
`track.album` is a **tier-1-only** field (see [entities](entities.md)); it is
`None` when the playlist could only be fetched from its embed page, so the
recipe falls back to an empty string rather than raising.

`max_tracks=None` fetches every track rather than the default 100 — drop it,
or lower it, for a large playlist you only want to sample.
