# Design: add-anonymous-token

## api/parse_embed.py (pure functions)

```python
def extract_next_data(html: str) -> dict[str, Any]
    # <script id="__NEXT_DATA__" type="application/json">...</script>; ParsingError if absent/bad JSON

def get_entity(next_data: Mapping[str, Any]) -> dict[str, Any]
    # props.pageProps.state.data.entity; NotFoundError if pageProps carries status/forbiddenReason
    # instead of state.data; ParsingError on unexpected shape

def get_session(next_data: Mapping[str, Any]) -> EmbedSession
    # props.pageProps.state.settings.session; ParsingError if missing fields

@dataclass(frozen=True, slots=True)
class EmbedSession:
    access_token: str
    expires_at_ms: int
    is_anonymous: bool
```

## auth/anonymous.py

```python
DEFAULT_BOOTSTRAP_ID = "4uLU6hMCjMI75M1A2tKUQC"  # any public track works
EXPIRY_SKEW_MS = 60_000

class AnonymousTokenProvider:
    def __init__(self, transport: Transport, *, bootstrap_track_id: str = DEFAULT_BOOTSTRAP_ID) -> None
    def token(self) -> str          # cached fast path; bootstraps via embed page when stale
    def invalidate(self) -> None    # next token() re-bootstraps

class AsyncAnonymousTokenProvider:  # mirror over AsyncTransport
```

- Staleness check is a pure helper `is_stale(expires_at_ms, now_ms)` so both variants share it.
- Bootstrap flow: `transport.get(embed_url("track", bootstrap_track_id))` → `extract_next_data` → `get_session`. Wrap `ParsingError`/`NetworkError` in `TokenError` (chained via `raise ... from`).
- Clock source injectable (`now_ms: Callable[[], int]`) for tests.
- `__repr__` of providers never includes the token.

## Testing

- `tests/unit/api/test_parse_embed.py`: all six fixtures parse; session extraction from each; dead-entity fixture (synthesize from the captured 2026 error shell shape: pageProps with `status`/`forbiddenReason`); ParsingError on garbage HTML.
- `tests/unit/auth/test_anonymous.py`: fake transport returning fixture HTML — cache hit (1 fetch for 2 token() calls), expiry-skew refresh (injected clock), invalidate(), TokenError on bad payload (message contains no token text).
