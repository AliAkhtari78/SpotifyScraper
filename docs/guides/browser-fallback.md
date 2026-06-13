# Browser fallback

The default HTTP transport (built on `httpx`) handles the vast majority of
requests. But on some networks or under aggressive anti-bot rules, Spotify may
serve a challenge page to plain HTTP clients. For those cases, SpotifyScraper
ships a **Playwright transport** that drives a real headless Chromium instance —
so requests carry a genuine browser's TLS/HTTP2 fingerprint and cookie jar.

You inject it with the `transport=` constructor argument; nothing else in your
code changes.

## When to use it

Reach for the browser transport only when the default fails — it is heavier
(it boots Chromium) and slower. Good signals:

- Persistent `NetworkError` / 403s from the GraphQL host that retries and proxies
  do not clear.
- Challenge or CAPTCHA pages returned to plain HTTP clients on your network.

If the default transport works for you, **keep it** — it is faster and has no
extra dependencies.

## Install

The browser transport lives behind the **`browser`** extra, and Playwright needs
a Chromium binary downloaded once:

```bash
pip install "spotifyscraper[browser]"
playwright install chromium
```

If you import the transport without the extra installed, you get a clear
`ImportError` pointing at both steps. If you install the extra but skip
`playwright install chromium`, the first request raises a Playwright error
telling you to download the browser.

## Use it

Construct a `PlaywrightTransport`, pass it as `transport=`, and let the client
drive it:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browser import PlaywrightTransport

transport = PlaywrightTransport(headless=True)
client = SpotifyClient(transport=transport)
try:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    print(track.name)
finally:
    client.close()
    transport.close()
```

!!! warning "You own the transport's lifecycle"
    When you inject a `transport=`, the client does **not** close it for you —
    that is by design, so you can reuse a browser across clients. Call
    `transport.close()` yourself (or use `try/finally` as above). The browser
    boots lazily on the first request, so constructing the transport is cheap.

## Constructor options

```python
PlaywrightTransport(
    *,
    headless=True,           # run Chromium headless; False to watch it
    proxy=None,              # e.g. "http://host:port"
    timeout=30.0,            # per-request timeout in seconds
    user_agent=None,         # override the browser User-Agent
    use_page_navigation=False,
)
```

| Option | Default | Notes |
|---|---|---|
| `headless` | `True` | Pass `False` to open a visible window while debugging. |
| `proxy` | `None` | Proxy URL applied to the browser context. |
| `timeout` | `30.0` | Per-request timeout, in seconds. |
| `user_agent` | `None` | Fixed User-Agent; Playwright's Chromium default is used when omitted. |
| `use_page_navigation` | `False` | Reserved knob; the default request-context path already handles both HTML and JSON. |

## Async browser transport

There is an async mirror, `AsyncPlaywrightTransport`, for the
[async client](async.md):

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient
from spotify_scraper.browser import AsyncPlaywrightTransport

async def main() -> None:
    transport = AsyncPlaywrightTransport(headless=True)
    client = AsyncSpotifyClient(transport=transport)
    try:
        track = await client.get_track("4uLU6hMCjMI75M1A2tKUQC")
        print(track.name)
    finally:
        await client.aclose()
        await transport.aclose()

asyncio.run(main())
```

## Errors

The browser transport raises the same library errors as the HTTP transport:
`NotFoundError` on 404, `RateLimitedError` on 429, and `NetworkError` on any
Playwright driver failure. Catch them exactly as in
[Error handling](error-handling.md).

!!! note "Rate limiting and the browser transport"
    The token-bucket rate limiter lives in the *HTTP* transport. When you inject
    a custom `transport=`, the client uses that transport's behavior instead, so
    the built-in `rate_limit` / `retry` knobs do not apply to the browser
    transport. Keep your request volume modest when using it.
