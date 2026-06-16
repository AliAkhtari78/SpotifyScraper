# http-transport Specification

## Purpose

The httpx-backed transport with retry and rate-limit handling.

## Requirements
### Requirement: Pluggable transport protocols

The library SHALL define `Transport` and `AsyncTransport` protocols with `get(url, *, headers) -> Response`, `close()`, and a shared minimal `Response` shape (`status_code: int`, `headers: Mapping[str, str]`, `text: str`, `content: bytes`, `json()`). Clients SHALL depend only on the protocols so alternative transports (e.g. a browser) can be injected.

#### Scenario: Custom transport injection

- **WHEN** a client is constructed with an object satisfying the protocol
- **THEN** all entity fetches use that object and no httpx code path is exercised

### Requirement: Retry with backoff

Transports SHALL retry failed requests according to `RetryPolicy(max_attempts, backoff_base, backoff_max)` using exponential backoff with jitter for connection errors, 5xx responses, and 429 responses. A 429 with a `Retry-After` value that exceeds the policy's remaining budget SHALL raise `RateLimitedError` carrying `retry_after` instead of sleeping.

#### Scenario: Transient server error

- **WHEN** a request receives a 503 and then a 200 on the next attempt
- **THEN** the caller receives the 200 response and no exception

#### Scenario: Hard rate limit

- **WHEN** a 429 response carries `Retry-After: 47231`
- **THEN** `RateLimitedError` is raised with `retry_after == 47231`

### Requirement: Client-side rate limiting

Transports SHALL throttle outgoing requests through a token bucket configured by `RateLimit(per_second, burst)`, with safe defaults (2 requests/second, burst 5). Sync and async implementations SHALL provide equivalent behavior.

#### Scenario: Burst exhaustion

- **WHEN** more requests than the burst size are issued instantly
- **THEN** excess requests are delayed rather than sent immediately

### Requirement: Browser-like identity and proxy support

Transports SHALL send a realistic browser `User-Agent` — chosen from a built-in pool (stable per transport instance) or overridden by the caller — alongside browser-consistent default headers, and SHALL support an optional proxy URL passed through to the underlying HTTP client.

#### Scenario: UA rotation across instances

- **WHEN** many transports are constructed without an explicit user agent
- **THEN** more than one distinct pool entry is observed across instances

### Requirement: Error mapping

Transport failures SHALL surface as `error-handling` types: connection/timeout errors as `NetworkError` (with the request URL attached), 404 as `NotFoundError`, and unrecoverable 429 as `RateLimitedError`. Raw httpx exceptions SHALL never escape.

#### Scenario: DNS failure

- **WHEN** the underlying client raises a connection error after retries are exhausted
- **THEN** the caller sees `NetworkError`, and `err.__cause__` is the original httpx exception

