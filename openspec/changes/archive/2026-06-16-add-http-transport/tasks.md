# Tasks: add-http-transport

## 1. Pure logic

- [x] 1.1 Implement `http/retry.py` (RetryPolicy + backoff_delay pure function)
- [x] 1.2 Implement `http/ratelimit.py` (RateLimit, TokenBucket, AsyncTokenBucket over shared pure math)
- [x] 1.3 Implement `http/headers.py` (UA pool, default headers)

## 2. Transports

- [x] 2.1 Implement `http/transport.py` (Response/Transport/AsyncTransport protocols, HttpxTransport, AsyncHttpxTransport, error mapping)

## 3. Tests

- [x] 3.1 `tests/unit/http/test_retry.py` and `test_ratelimit.py` (pure-function tables)
- [x] 3.2 `tests/unit/http/test_transport.py` and `test_transport_async.py` (respx)

## 4. Verify

- [x] 4.1 `make lint`, `make type`, `make test` green
