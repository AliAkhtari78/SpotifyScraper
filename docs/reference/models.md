# Models

Every entity is a frozen, slotted dataclass. Fields that only the tier-1
pathfinder payload can supply are typed `| None`, so a value of `None` means
"not available from the source that answered", not "empty". Every model has a
JSON-safe `to_dict()`.

!!! note "Reserved for v3.1"
    `Lyrics` and `LyricsLine` are defined but **not populated** in v3.0.0.
    Cookie-authenticated lyrics extraction ships in v3.1; their fields are
    reserved until then.

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

## Lyrics (reserved for v3.1)

::: spotify_scraper.models.Lyrics

## LyricsLine (reserved for v3.1)

::: spotify_scraper.models.LyricsLine
