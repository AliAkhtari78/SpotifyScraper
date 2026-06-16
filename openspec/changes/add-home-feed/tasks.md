# Tasks: add-home-feed

## 1. Feasibility spike (go/no-go)

- [ ] 1.1 Capture the live authenticated `pathfinder/v2/query` POST for `home`
      (chrome-devtools + real `sp_dc`): request body, `homeEndUserIntegration`
      value/shape, persisted-query `sha256`, response JSON shape
- [ ] 1.2 Save a scrubbed fixture; record the verified shape in the endpoints reference
- [ ] 1.3 **Decision:** reproducible on the v2 POST path → proceed; else keep deferred

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
