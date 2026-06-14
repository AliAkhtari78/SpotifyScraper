# Tasks: add-browser-login

> Branch off `add-podcast-transcripts` (HEAD) so the `_cookie_*` names are present.

## 0. Live verification (gates ONLY the headed-login UX — maintainer must run)

- [ ] 0.1 With a real Spotify account, run `capture_sp_dc()` end to end: confirm a
      headed Chromium opens, the manual login completes, and the `sp_dc` cookie is
      captured from `context.cookies("https://open.spotify.com/")` (NOT via
      `wait_for_url`). Record the typical post-login landing URL(s) so docs are right.
- [ ] 0.2 Confirm the captured cookie mints a valid web-player token: feed it to
      `SpotifyClient(cookies=<captured>)` and call `get_lyrics`/`get_transcript`.
- [ ] 0.3 Time the slowest realistic path (2FA / CAPTCHA / region interstitial) and
      confirm the default `timeout=300.0` is generous enough; adjust the documented
      default if not. Note in design.md.
- [ ] 0.4 Confirm closing the browser window WITHOUT clicking "Log out" leaves
      `sp_dc` valid server-side (logging out invalidates it). Document the warning.
- [ ] 0.5 Decide the persistent-profile question: throwaway `mkdtemp` profile
      deleted after capture (recommended — single secret store) vs. a kept profile.
      Record the decision; v1 default = throwaway temp profile, `shutil.rmtree`'d.

## 1. Errors

- [ ] 1.1 Add `class SessionError(SpotifyScraperError)` to `errors.py` with a
      docstring ("saved session is missing, unreadable, insecurely permissioned, or
      expired"). Export it from `spotify_scraper.errors` and the top-level package
      `__init__.py` (`__all__`, alphabetical).

## 2. Session store (sans-io, stdlib only)

- [ ] 2.1 Create `src/spotify_scraper/auth/session.py`. Module constants:
      `_APP_DIR_NAME="spotifyscraper"`, `_SESSION_FILENAME="session.json"`,
      `_SCHEMA_VERSION=1`, and three hints (`_MISSING_HINT`, `_CORRUPT_HINT`,
      `_INSECURE_HINT`) that NEVER embed cookie content (a bare path is fine).
- [ ] 2.2 Frozen, slotted `Session(sp_dc: str, saved_at_ms: int,
      sp_dc_expires_ms: int | None = None, version: int = _SCHEMA_VERSION)` with a
      cookie-free `__repr__`, JSON-safe `to_dict()`, and a validating `from_dict()`
      that raises `SessionError(_CORRUPT_HINT)` on wrong/missing types.
- [ ] 2.3 `default_config_dir()` — hand-rolled, stdlib only. Precedence:
      `SPOTIFYSCRAPER_CONFIG_DIR` → `XDG_CONFIG_HOME` → platform default via
      `sys.platform` (`~/.config` Linux, `~/Library/Application Support` macOS,
      `%APPDATA%` Windows). `default_session_path()` returns
      `default_config_dir() / _SESSION_FILENAME`. NO `platformdirs` dependency.
- [ ] 2.4 `save_session(sp_dc, *, sp_dc_expires_ms=None, path=None, now_ms=...) -> Path`:
      `makedirs(dir, mode=0o700, exist_ok=True)`; `tempfile.mkstemp(dir=...)` (0600
      from first byte); write JSON via `os.fdopen`; `os.replace(tmp, path)` (atomic,
      same filesystem); `os.unlink(tmp)` + re-raise on any failure. Return the path.
- [ ] 2.5 `load_session(*, path=None) -> Session`: `SessionError(_MISSING_HINT)` if
      absent; on POSIX (`os.name == "posix"`) `SessionError(_INSECURE_HINT)` if
      `os.stat(path).st_mode & 0o077` is nonzero (REFUSE — do NOT auto-chmod; skip
      this check on Windows where mode bits are no-ops and AppData is per-user ACL'd);
      `SessionError(_CORRUPT_HINT)` on bad JSON / missing `sp_dc` / wrong type.
- [ ] 2.6 `clear_session(*, path=None) -> None`: idempotent delete (no error when
      absent) for one-call local revocation.
- [ ] 2.7 Define a small `SessionStore` indirection (a Protocol or a `store=` string
      dispatch) selecting the file backend by default; design it so the keyring
      backend (task 3) drops in without touching callers.

## 3. Optional keyring backend

- [ ] 3.1 Create `src/spotify_scraper/auth/session_keyring.py` with a lazy
      `import keyring` inside the functions, raising a helpful `ImportError`
      ("install spotifyscraper[keyring]") when absent.
- [ ] 3.2 Store ONLY `sp_dc` in the keyring (`keyring.set/get/delete_password(
      "spotifyscraper", "sp_dc", ...)`) to stay under the Windows Credential Locker
      ~1280-char limit; keep non-secret metadata (`saved_at_ms`, expiry, version) in
      the 0600 JSON file via the file backend.
- [ ] 3.3 On `keyring.errors.NoKeyringError` (headless Linux, no Secret Service),
      fall back to the file backend with a `logging.warning` (never crash, never log
      the value). Backend choice is EXPLICIT (`store="file"|"keyring"`), never
      silently switched based on what is pip-installed.
- [ ] 3.4 `pyproject.toml`: add `keyring = ["keyring>=24"]` to optional-dependencies;
      add it to `all = ["spotifyscraper[media,browser,cli,keyring]"]`.

## 4. Browser-assisted login (browser extra, lazy Playwright)

- [ ] 4.1 Create `src/spotify_scraper/browser/login.py`. Top-level imports
      `from playwright.sync_api import sync_playwright` and the async twin (the
      lazy-import guard lives in `browser/__init__.py`). Constants: `LOGIN_URL=
      "https://accounts.spotify.com/login"`, `HOME_URL="https://open.spotify.com/"`,
      `_DEFAULT_TIMEOUT_S=300.0`, `_NO_COOKIE_HINT`.
- [ ] 4.2 `capture_sp_dc(*, timeout=_DEFAULT_TIMEOUT_S, proxy=None) -> str`: launch
      `chromium.launch(headless=False, proxy=...)` (ALWAYS headed), `new_context()`,
      `new_page()`, `goto(LOGIN_URL)`; poll `context.cookies(HOME_URL)` every ~1s
      against a `time.monotonic()` deadline; return the first non-empty `sp_dc`
      value; always `context.close()`/`browser.close()` in a `finally`. Raise
      `AuthenticationError(_NO_COOKIE_HINT)` on timeout/none. Catch Playwright
      `Error`/`TimeoutError` and re-raise as `AuthenticationError(_NO_COOKIE_HINT)`
      WITHOUT leaking the cookie or a stack. Never log the value.
- [ ] 4.3 `capture_sp_dc_async(...)` — 1:1 async mirror using `async_playwright()`
      and `asyncio.sleep` for the poll loop.
- [ ] 4.4 Update `browser/__init__.py`: re-export `capture_sp_dc`,
      `capture_sp_dc_async` inside the existing `try/except ImportError` block; add
      both to `__all__`.

## 5. Client entry points (both clients)

- [ ] 5.1 `_sync/client.py` — add `login(self, *, save=True, store="file",
      timeout=300.0, proxy=None, session_path=None) -> None`: `self._ensure_open()`;
      `from spotify_scraper.browser import capture_sp_dc` (method-level lazy import);
      `sp_dc = capture_sp_dc(timeout=timeout, proxy=proxy)`; set `self._cookies =
      sp_dc`; `self._cookie_tokens = None` (force re-exchange); when `save`,
      `save_session(sp_dc, path=session_path)` via the chosen `store`. (Note: neither
      client stores `proxy` as a slot — it is consumed at construction — so `login`
      takes an explicit `proxy=` param rather than reading a nonexistent slot.)
- [ ] 5.2 `_sync/client.py` — add `from_saved_session(cls, *, store="file",
      session_path=None, **kwargs) -> SpotifyClient` classmethod: `load_session(...)`,
      then `cls(cookies=session.sp_dc, **kwargs)`. And `logout(cls, *, store="file",
      session_path=None) -> None` calling `clear_session(...)`.
- [ ] 5.3 `_async/client.py` — `async def login(...)` awaiting `capture_sp_dc_async`;
      `from_saved_session`/`logout` stay sync classmethods (file-only reads) returning
      `AsyncSpotifyClient`.
- [ ] 5.4 Export the session API (`Session`, `save_session`, `load_session`,
      `clear_session`, `default_session_path`) from `auth/__init__.py`.

## 6. CLI (optional, cli extra)

- [ ] 6.1 Add a `login` command to `cli/main.py`: call `capture_sp_dc()` then
      `save_session()`, print ONLY the saved path (never the cookie). Clear message
      when the `browser` extra is missing. Honor a `--store file|keyring` option.
- [ ] 6.2 Add a `logout` command calling `clear_session()`; print the cleared path.

## 7. Tests

- [ ] 7.1 `tests/unit/auth/test_session.py` (default suite, hermetic): round-trip
      `save_session`/`load_session` into `tmp_path`; assert 0600 perms on POSIX;
      `load_session` raises `SessionError(_MISSING_HINT)` when absent,
      `_CORRUPT_HINT` on malformed JSON, `_INSECURE_HINT` when the file is
      group/world-readable (POSIX); assert `repr(Session(...))`, `to_dict()` keys,
      and every error string NEVER contain the cookie value; `clear_session` is
      idempotent; `default_config_dir()` honors `SPOTIFYSCRAPER_CONFIG_DIR` then
      `XDG_CONFIG_HOME` via `monkeypatch.setenv`.
- [ ] 7.2 `tests/unit/auth/test_session_keyring.py` (default suite): monkeypatch a
      fake `keyring` module; assert only `sp_dc` is stored in it and metadata lands
      in the JSON file; assert the helpful `ImportError` when `keyring` is absent;
      assert `NoKeyringError` falls back to the file backend.
- [ ] 7.3 `tests/unit/test_client_login.py` (default suite, sync + async):
      monkeypatch `spotify_scraper.browser.capture_sp_dc[_async]` to return a fake
      `sp_dc`; assert `login(save=False)` sets `self._cookies` and resets
      `_cookie_tokens` with ZERO network calls; assert `login(save=True,
      session_path=tmp)` writes a loadable session; `from_saved_session(
      session_path=tmp)` builds a working client and forwards `**kwargs`;
      `from_saved_session` raises `SessionError` when the file is missing; `logout`
      removes the file; `login` after `close()` raises `SpotifyScraperError`.
- [ ] 7.4 `tests/unit/cli/test_cli_login.py` (default suite): FakeClient/fake capture;
      assert the printed output contains the saved path and NEVER the cookie; assert
      exit codes; assert the missing-`browser`-extra message.
- [ ] 7.5 Extend the ImportError test in `tests/browser/test_playwright_transport.py`
      (or a sibling) to assert `capture_sp_dc`/`capture_sp_dc_async` also raise the
      helpful `ImportError` when `playwright` is absent.
- [ ] 7.6 `tests/browser/test_login.py` (`@pytest.mark.browser`, excluded by
      default): real headed-Chromium smoke test of `capture_sp_dc(timeout=<short>)`
      asserting `AuthenticationError` when no login occurs (a real Spotify login
      cannot be scripted in CI).

## 8. Packaging & coverage

- [ ] 8.1 `pyproject.toml` `[tool.coverage.run] omit`: add
      `src/spotify_scraper/browser/login.py` next to `playwright.py`.

## 9. Verify

- [ ] 9.1 `make lint`, `make type`, `make test`, `make cov` (≥85%) all green.
- [ ] 9.2 Run the maintainer live checks 0.1–0.5; confirm captured `sp_dc` works and
      the timeout/profile decisions hold.
- [ ] 9.3 Docs: add an "Authenticated sessions" page — `login()` is interactive/
      desktop only (needs a display); `from_saved_session()` is the headless-server
      path; the keyring extra; the "don't click Log out" warning; revocation via
      `logout()`/`clear_session()` or deleting the file.