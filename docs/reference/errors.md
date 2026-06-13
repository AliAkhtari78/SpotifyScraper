# Errors

Every exception the library raises derives from `SpotifyScraperError`, so a
single `except SpotifyScraperError` catches all library failures. The
[Error handling guide](../guides/error-handling.md) covers the catch patterns.

The hierarchy:

```text
SpotifyScraperError
├── URLError
├── NetworkError
│   └── RateLimitedError
├── TokenError
├── AuthenticationError
├── NotFoundError
├── ParsingError
└── MediaError
```

## SpotifyScraperError

::: spotify_scraper.errors.SpotifyScraperError

## URLError

::: spotify_scraper.errors.URLError

## NetworkError

::: spotify_scraper.errors.NetworkError

## RateLimitedError

::: spotify_scraper.errors.RateLimitedError

## TokenError

::: spotify_scraper.errors.TokenError

## AuthenticationError

::: spotify_scraper.errors.AuthenticationError

## NotFoundError

::: spotify_scraper.errors.NotFoundError

## ParsingError

::: spotify_scraper.errors.ParsingError

## MediaError

::: spotify_scraper.errors.MediaError
