# Design: add-browser-fallback

## browser/__init__.py

Try-import guard: `from spotify_scraper.browser.playwright import PlaywrightTransport, AsyncPlaywrightTransport` wrapped so a missing playwright package raises
`ImportError("Browser transport requires the 'browser' extra: pip install spotifyscraper[browser] && playwright install chromium")`.

## browser/playwright.py

```python
class _BrowserResponse:            # satisfies the Response protocol
    status_code: int; headers: Mapping[str, str]; text: str; content: bytes; json()

class PlaywrightTransport:
    def __init__(self, *, headless: bool = True, proxy: str | None = None,
                 timeout: float = 30.0, user_agent: str | None = None) -> None
    def get(self, url, *, headers=None) -> _BrowserResponse
    def close(self) -> None
```

- Lazy start: first `get()` boots `sync_playwright().start()` → chromium.launch → context (UA, proxy).
- Fetch strategy: `context.request.get(url, headers=...)` (Playwright's APIRequestContext shares the browser's TLS/HTTP2 fingerprint and cookies) — robust for both HTML and JSON; fall back to `page.goto` only if needed for challenge pages (document the knob `use_page_navigation: bool = False`).
- Error mapping mirrors HttpxTransport: 404→NotFoundError, 429→RateLimitedError, driver errors→NetworkError. Reuse `backoff_delay`/token bucket? Keep it simple: no client-side rate limit in the browser transport (the browser is already slow); retries via the same RetryPolicy loop extracted to a shared helper if trivial, else one attempt + documented behavior. Decision: share the retry loop by extracting `http/_retry_loop.py` ONLY if it needs no async forking gymnastics; otherwise single-attempt with clear docs.
- Async variant via `async_playwright()`.

## CI

`ci.yml` gains an independent, non-blocking job `browser` (ubuntu, 3.13): `uv sync --locked --extra browser`, `uv run playwright install --with-deps chromium`, run `tests/browser/` (marked `browser`, excluded from default addopts alongside `live`)... CI job runs `uv run pytest -m browser`, which performs one live track fetch through the transport. Scheduled-canary inclusion: no (keep canary fast); manual dispatch covers it.

## Testing

`tests/browser/test_playwright_transport.py` (`@pytest.mark.browser`): protocol satisfaction (isinstance runtime_checkable), live embed fetch returns parseable `__NEXT_DATA__`, pathfinder JSON via client with injected transport, ImportError message test via monkeypatched missing module (this one runs in the default suite).
Marker registration: add `browser` to pytest markers; default addopts becomes `-m "not live and not browser"`.
