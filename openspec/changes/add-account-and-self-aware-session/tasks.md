# Tasks: add-account-and-self-aware-session

## 0. Live verification (informs parse_account / _account_bool — do with maintainer)

- [ ] 0.1 With the maintainer `SPOTIFY_SP_DC`, capture a real response from
      `GET https://spclient.wg.spotify.com/melody/v1/product_state` with headers
      `Authorization: Bearer <cookie-derived token>`, `app-platform: WebPlayer`.
      Confirm 200 `application/json` and a FLAT object.
- [ ] 0.2 Record the exact keys and value types actually returned: `product`,
      `catalogue`, `country`, `on-demand` (string `"1"` vs JSON `true`?),
      `preferred-locale`, `selected-language`; note any extras
      (`ads`, `is-standalone-audiobooks`, `multiuserplan-*`) — captured for
      reference but NOT modeled in v1.
- [ ] 0.3 Confirm the non-200 split (expect 401 = bad/expired token → drives the
      retry). Note in design.md.
- [ ] 0.4 Scrub the captured body (no `accessToken`/`clientId`/cookie/PII) into a
      synthetic fixture and pin it in design.md as the contract `parse_account`
      targets.

## 1. Account model

- [ ] 1.1 Create `src/spotify_scraper/models/account.py`: frozen, slotted
      `Account(ModelBase)` with fields `product`, `catalogue`, `country`,
      `on_demand`, `preferred_locale`, `selected_language` (all `| None`,
      defaulting `None`) and a derived `is_premium` **property**
      (`return self.product == "premium"`). Docstring notes the property is not
      a wire field and is absent from `to_dict()`.
- [ ] 1.2 Export `Account` from `models/__init__.py` (import + `__all__`, first
      entry alphabetically) and from top-level `__init__.py` (import block +
      `__all__`, between `Album` and `AlbumRef`).

## 2. Sans-io endpoint + parser

- [ ] 2.1 Create `src/spotify_scraper/api/account.py` mirroring `api/lyrics.py`:
      module-private `_PRODUCT_STATE_URL`, `product_state_url()` (NO arg),
      `auth_headers(token)`. Pure / I/O-free. Endpoint lives ONLY here.
- [ ] 2.2 Add `parse_account(payload)` to `api/parse_entities.py`: import
      `Account`, add `"parse_account"` to `__all__` (sorted, before
      `parse_album_embed`), new `# Account` section, reuse `_optional_str`, map
      hyphen→snake here, use a new tolerant `_account_bool` for `on-demand`. No
      `ParsingError` shape gate (flat body, every field independently optional).
- [ ] 2.3 Add `_account_bool(value)` near `_optional_bool`: `None` if absent/
      unparseable; `True` for `True`/`"1"`/`"true"`; `False` for `False`/`"0"`/
      `"false"` (case-insensitive). Keep tolerant per the captured wire type.

## 3. Client exposure — account (shared provider)

- [ ] 3.1 Sync `_sync/client.py`: add imports `from spotify_scraper.api import
      account as account_api` and `from spotify_scraper.models.account import
      Account`. Add public `get_account()` + `is_premium()` after
      `get_transcript`, and private `_fetch_account(token)` after
      `_fetch_transcript`. Route through `self._cookie_provider()`,
      401→invalidate+retry-once, non-JSON→`ParsingError`. No `_resolve`, no
      `NotFoundError` remap, no envelope decode.
- [ ] 3.2 Async `_async/client.py`: mirror 3.1 with `async def`, `await
      provider.token()`, `await self._transport.get(...)`;
      `is_premium` becomes `return (await self.get_account()).is_premium`.

## 4. Self-aware session helpers

- [ ] 4.1 `auth/session.py`: add frozen, slotted `SessionInfo(exists, valid,
      saved_at_ms=None, sp_dc_expires_ms=None, reason=None)` (cookie-free; NOT a
      `ModelBase`). Add `session_info(*, path=None, now_ms=None)` (catch
      `SessionError` → flags + cookie-free `reason`; expired → `valid=False`
      with reason; else `valid=True`) and `has_saved_session(*, path=None,
      now_ms=None)` returning `.valid`. Reuse `load_session`, `_resolve_path`,
      `_default_now_ms`.
- [ ] 4.2 `auth/session.py` `SessionStore`: add `info(*, path=None, now_ms=None)`
      and `has_session(*, path=None, now_ms=None)` delegating to file vs keyring
      backend, mirroring `save`/`load`/`clear`.
- [ ] 4.3 `auth/session_keyring.py`: add `keyring_info(*, path=None, now_ms=None)`
      mirroring `load_from_keyring` wrapped in the SessionError→`SessionInfo`
      shape; if the OS keyring is absent, return a file-backed `SessionInfo`
      (metadata file existence + validity) with a cookie-free reason.

## 5. Client login auto-skip + optional introspection

- [ ] 5.1 Sync `_sync/client.py` `login`: add `reuse: bool = True` keyword
      (first). When `reuse and backend.has_session(path=session_path)`: load the
      session, set `self._cookies`, `self._cookie_tokens = None`, return — browser
      never opens. Move `from spotify_scraper.browser import capture_sp_dc`
      INSIDE the non-reuse branch. Update the docstring (document `reuse` and the
      auto-skip sentence).
- [ ] 5.2 Async `_async/client.py` `login`: mirror 5.1 with
      `capture_sp_dc_async` + `await`. `has_session`/`load` stay sync (no await).
- [ ] 5.3 (Optional) Add a `session_info(*, store="file", session_path=None)`
      classmethod to both clients beside `from_saved_session`/`logout`, returning
      `SessionStore(store).info(path=session_path)`. Import `SessionInfo`.
- [ ] 5.4 (Optional, only if surfaced publicly) Export `SessionInfo` from
      top-level `__init__.py` (import + `__all__`). Otherwise leave internal,
      reachable via `client.session_info()`.

## 6. Cookie-expiry capture (optional — gates real "days remaining")

- [ ] 6.1 (Optional) In `browser/login.py`, surface the captured cookie's
      `expires` (epoch seconds) alongside the value, and thread it into the
      `login()` `backend.save(sp_dc, sp_dc_expires_ms=<ms>, ...)` call (the store
      already accepts `sp_dc_expires_ms`). If skipped, document that days-remaining
      is unavailable for sessions saved without an expiry, and `SessionInfo`
      omits it.

## 7. CLI (optional, mirrors login/logout)

- [ ] 7.1 (Optional) Add a `session`/`status` command to `cli/main.py` printing
      `SessionStore(store).info()` fields (exists/valid/saved_at/expiry/days-
      remaining) — NEVER the cookie. Wire `--reuse/--no-reuse` into the `login`
      command's call path.

## 8. Tests

- [ ] 8.1 NEW `tests/unit/api/test_parse_account.py`: table-test `parse_account`
      over the synthetic fixture — full hyphenated body → all fields + `is_premium`
      True; `product="free"` → `is_premium` False; `{}` → all `None`, `is_premium`
      False; `"on-demand": "1"` → `True`, `"0"` → `False`. Pure / hermetic.
- [ ] 8.2 NEW `tests/unit/test_client_account.py` (respx, sync + async): reuse
      `_mock_token_handshake`/`_token_body`; mock
      `PRODUCT_STATE_RE = re.compile(r"https://spclient\.wg\.spotify\.com/melody/v1/product_state.*")`.
      Cover: no-cookies → `AuthenticationError` with **0 router calls**; success
      asserts `Authorization`/`app-platform` headers + `is_premium`; 401 →
      invalidate + retry once (`token_route.call_count == 2`); anonymous cookie →
      `AuthenticationError`; use-after-close.
- [ ] 8.3 Extend a model round-trip test:
      `Account.from_dict(account.to_dict()) == account`, asserting `is_premium`
      is absent from `to_dict()`.
- [ ] 8.4 Extend `tests/unit/auth/test_session.py`: `session_info`/
      `has_saved_session` with `tmp_path` + injected `now_ms` — missing →
      `exists=False, valid=False`; freshly saved no-expiry → `valid=True`;
      `sp_dc_expires_ms` in the past → `exists=True, valid=False, reason` set;
      POSIX `chmod 0o644` → `valid=False` (skip on Windows); corrupt JSON →
      `valid=False`. Assert `repr(SessionInfo(...))` and `reason` contain no
      cookie substring.
- [ ] 8.5 Extend `tests/unit/test_client_login.py` (+ async mirror): `login(
      reuse=True)` with a pre-saved valid session → monkeypatched
      `capture_sp_dc` is **never called**, `client._cookies == saved_sp_dc`,
      `client._cookie_tokens is None`. `login(reuse=False)` (or no saved session)
      still calls the patched capture and saves (existing cases stay green).
- [ ] 8.6 (If 5.3/5.4 done) Test the client `session_info()` classmethod over a
      `tmp_path` session. (If 7.1 done) `tests/unit/cli/` test for the
      `session`/`status` command: prints fields, never the cookie, exit codes.
- [ ] 8.7 NEW `tests/live/test_account.py`: `pytestmark =
      pytest.mark.skipif(not os.environ.get("SPOTIFY_SP_DC"), ...)`,
      `@pytest.mark.live`, sync + async — `account = client.get_account()`,
      assert `account.country` truthy, `account.product in {"premium","free",
      "open"}`, `client.is_premium() == account.is_premium`.

## 9. Verify

- [ ] 9.1 `make lint`, `make type`, `make test`, `make cov` (≥85%) all green.
- [ ] 9.2 `make live` (with `SPOTIFY_SP_DC`) green; confirm captured product_state
      still matches `parse_account`/`_account_bool`.
- [ ] 9.3 Docs: add `get_account`/`is_premium` to the authenticated-features page
      next to lyrics/transcripts; document `login(reuse=...)` and
      `session_info`/`has_saved_session`.

## 10. Review fixes

- [x] 10.1 `keyring_info` probes the OS keyring secret (lazy import; skipped
      without the extra), so a valid metadata file whose keyring entry is gone
      reports `valid=False` and `has_session()` stays honest.
- [x] 10.2 Guard the `login(reuse=True)` branch (sync + async) to fall through to
      browser capture when the saved secret is empty or unloadable, rather than
      wiring `sp_dc=""`. The CLI reuse branch is corrected by the keyring probe.
- [x] 10.3 Add `SessionInfo.to_dict()` (cookie-free, JSON-safe).
- [x] 10.4 Tests: async account failures (empty body, 2nd-401 → AuthenticationError,
      non-JSON → ParsingError); `keyring_info` invalid when secret gone;
      reuse falls through on an empty secret (sync + async); `SessionInfo.to_dict()`.
- [ ] 10.5 Docs: `get_account`/`is_premium`, `login(reuse=...)`, `session_info`/
      `session` CLI, and the keyring `ImportError` note in the authentication guide;
      `Account` autodoc; index + README + CHANGELOG.