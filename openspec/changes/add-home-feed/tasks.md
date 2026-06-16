# Tasks: add-home-feed

## 1. Feasibility spike (go/no-go) — RAN 2026-06-16

- [x] 1.1 Spike ran (chrome-devtools + Playwright + persisted `sp_dc`). Automated
      capture is **blocked**: the web SPA never bootstraps Home with an injected
      `sp_dc` (blank render, no `pathfinder`/`/api/token` calls), and `pathfinder/v2/query`
      returns an edge `403` for the v1-style auth (the web client uses a `clienttoken`).
- [ ] 1.2 (blocked) Capture the real request — needs an *interactive* real-browser
      login + a cleared IP edge-block; not achievable via automation.
- [x] 1.3 **Decision: NO-GO — keep Home deferred.** See `design.md` → "Spike result".
      Shipping would also require a `clienttoken` device handshake (protobuf), at
      odds with the one-runtime-dep core. Revisit only if Home becomes a priority.

## 2. Transport (POST)

- [ ] 2.1 Add `post()` to `Transport` / `AsyncTransport` protocols + `HttpxTransport` /
      `AsyncHttpxTransport` (reuse retry + per-host rate-limit; mirror sync+async)
- [ ] 2.2 Pass POST through `CachingTransport` / `AsyncCachingTransport` uncached

## 3. Pathfinder v2 + parsing

- [ ] 3.1 `PATHFINDER_V2_URL` + `home` operation + `build_post_request()` in `api/pathfinder.py`
- [ ] 3.2 `parse_home()` in `api/parse_entities.py` (defensive, skips unknown item types)
- [ ] 3.3 `Home` / `HomeSection` / `HomeItem` models with `to_dict()`; export them

## 4. Client + tooling

- [ ] 4.1 `get_home()` on `_sync` and `_async` clients (user-token path; anon → `AuthenticationError`)
- [ ] 4.2 `home` CLI command; `get_home` MCP tool (authenticated)

## 5. Docs + tests + release

- [ ] 5.1 README + docs guide + mkdocs nav + model autodoc + CHANGELOG + wiki
- [ ] 5.2 Hermetic unit test (scrubbed fixture) + `@pytest.mark.live` test; ≥85% cov; mypy --strict
- [ ] 5.3 Bump `__version__`; tag/release; verify ghcr image build
