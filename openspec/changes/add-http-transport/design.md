# Design: add-http-transport

## Shapes

```python
# http/transport.py
class Response(Protocol):            # structural; httpx.Response satisfies it
    status_code: int
    @property
    def headers(self) -> Mapping[str, str]: ...
    @property
    def text(self) -> str: ...
    @property
    def content(self) -> bytes: ...
    def json(self) -> Any: ...

@runtime_checkable
class Transport(Protocol):
    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response: ...
    def close(self) -> None: ...

@runtime_checkable
class AsyncTransport(Protocol):
    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response: ...
    async def aclose(self) -> None: ...

class HttpxTransport:                # and AsyncHttpxTransport mirroring it
    def __init__(self, *, rate_limit: RateLimit | None = None, retry: RetryPolicy | None = None,
                 user_agent: str | None = None, proxy: str | None = None,
                 timeout: float = 10.0) -> None: ...
```

```python
# http/retry.py
@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 4
    backoff_base: float = 0.5
    backoff_max: float = 30.0

def backoff_delay(policy: RetryPolicy, attempt: int, retry_after: float | None) -> float | None
# pure function: None => give up. Honors retry_after if <= backoff_max budget; jitter via random.uniform(0, 0.25*delay).
```

```python
# http/ratelimit.py
@dataclass(frozen=True, slots=True)
class RateLimit:
    per_second: float = 2.0
    burst: int = 5

class TokenBucket:        # threading.Lock; .acquire() sleeps as needed
class AsyncTokenBucket:   # asyncio.Lock; await .acquire()
# Shared pure helper computes (new_tokens, wait_seconds) from (tokens, last_refill, now, config) —
# the sync/async classes only differ in how they sleep.
```

```python
# http/headers.py
USER_AGENTS: tuple[str, ...]   # ~8 current real browser UA strings (Chrome/Firefox/Safari, mac/win/linux)
def pick_user_agent() -> str   # random.choice — chosen once per transport instance
def default_headers(user_agent: str) -> dict[str, str]
    # Accept, Accept-Language: en, User-Agent
```

## Decisions

- **Sans-io discipline**: backoff math and token-bucket math are pure functions; only the transports sleep (`time.sleep` / `asyncio.sleep`). Tests cover the pure functions exhaustively and the transports via respx.
- **Retry on**: httpx.ConnectError/ConnectTimeout/ReadTimeout/RemoteProtocolError, 5xx, 429. Not on other 4xx.
- **404 → NotFoundError** is raised by the transport (entity-agnostic message; extractors may re-raise with context).
- **Proxy**: passed as `httpx.Client(proxy=...)`. No env-var magic — explicit only.
- Headers param merges over defaults (caller wins).

## Testing

`tests/unit/http/`: `test_retry.py` (pure backoff table: attempts, retry_after honoring, give-up), `test_ratelimit.py` (bucket math, monotonic clock injection), `test_transport.py` + `test_transport_async.py` (respx: success, 503-then-200 retry, 429 hard raise, 404 mapping, connection-error mapping, UA pool rotation across instances, custom header merge).
