# Models

Every entity is a frozen, slotted dataclass. Fields that only the tier-1
pathfinder payload can supply are typed `| None`, so a value of `None` means
"not available from the source that answered", not "empty". Every model has a
JSON-safe `to_dict()`.

!!! note "Some models need a cookie"
    `Lyrics`/`LyricsLine` and `Transcript`/`TranscriptLine` are populated by
    [`get_lyrics`](client.md) and [`get_transcript`](client.md), which require a
    user `sp_dc` cookie — see the
    [lyrics & cookies guide](../guides/lyrics-and-cookies.md).

## Track

::: spotify_scraper.models.Track

## Album

::: spotify_scraper.models.Album

## Artist

::: spotify_scraper.models.Artist

## Playlist

::: spotify_scraper.models.Playlist

## PlaylistTrack

::: spotify_scraper.models.PlaylistTrack

## Episode

::: spotify_scraper.models.Episode

## Show

::: spotify_scraper.models.Show

## Image

::: spotify_scraper.models.Image

## ArtistRef

::: spotify_scraper.models.ArtistRef

## AlbumRef

::: spotify_scraper.models.AlbumRef

## ShowRef

::: spotify_scraper.models.ShowRef

## UserRef

::: spotify_scraper.models.UserRef

## Lyrics

::: spotify_scraper.models.Lyrics

## LyricsLine

::: spotify_scraper.models.LyricsLine

## Transcript

::: spotify_scraper.models.Transcript

## TranscriptLine

::: spotify_scraper.models.TranscriptLine
