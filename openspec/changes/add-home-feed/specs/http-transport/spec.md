# http-transport

## ADDED Requirements

### Requirement: POST request support

The transport layer SHALL expose a `post(url, *, headers, json)` method on both the
synchronous and asynchronous transports, sending a JSON request body and applying
the same retry, per-host rate-limit, and error-classification handling as `get`.
POST responses SHALL NOT be cached; the caching transport SHALL delegate POST
straight through to the underlying transport.

#### Scenario: JSON body POST

- **WHEN** a caller issues a `post()` with a JSON body to the pathfinder v2 endpoint
- **THEN** the request is sent with the body as JSON and the response is returned with the same retry/rate-limit handling as `get()`

#### Scenario: POST is never cached

- **WHEN** a `post()` is issued through the caching transport
- **THEN** the request is delegated to the underlying transport and no response is read from or written to the cache
