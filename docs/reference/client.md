# Client

`SpotifyClient` is the synchronous facade. It owns an HTTP transport and an
anonymous token provider, exposes one `get_*` method per entity type plus the
media download helpers, and works as a context manager. See the
[Entities guide](../guides/entities.md) for task-oriented examples.

::: spotify_scraper.SpotifyClient
