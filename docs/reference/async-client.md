# Async client

`AsyncSpotifyClient` is a 1:1 async mirror of [`SpotifyClient`](client.md): the
same methods, the same return models, but `async`/`await` over an async
transport. It is an async context manager — use `async with` or call
`aclose()`. See the [Async guide](../guides/async.md) for `gather` patterns.

::: spotify_scraper.AsyncSpotifyClient
