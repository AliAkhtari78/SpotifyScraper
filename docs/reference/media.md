# Media

The simplest way to download cover art and preview audio is through the client
methods `download_cover()` and `download_preview()` (shown below). They wrap the
transport-driven helpers in `spotify_scraper.media`, which the sync and async
facades share. Cover embedding needs the `media` extra (`mutagen`); install it
with `pip install "spotifyscraper[media]"`. See the
[Media downloads guide](../guides/media-downloads.md) for examples.

## Client methods

::: spotify_scraper.SpotifyClient.download_cover

::: spotify_scraper.SpotifyClient.download_preview

## Async client methods

::: spotify_scraper.AsyncSpotifyClient.download_cover

::: spotify_scraper.AsyncSpotifyClient.download_preview

## Helper functions

These are the lower-level functions the client methods delegate to; reach for
them only if you are driving a transport yourself.

::: spotify_scraper.media.download_cover_sync

::: spotify_scraper.media.download_cover_async

::: spotify_scraper.media.download_preview_sync

::: spotify_scraper.media.download_preview_async

::: spotify_scraper.media.pick_image

::: spotify_scraper.media.safe_filename

::: spotify_scraper.media.extension_from_content_type
