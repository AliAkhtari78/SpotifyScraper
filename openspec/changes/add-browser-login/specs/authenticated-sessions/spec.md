# authenticated-sessions

## ADDED Requirements

### Requirement: Browser-assisted sp_dc capture (no password)

The library SHALL provide a browser-assisted login that captures the `sp_dc`
cookie after a user signs in manually, and SHALL NEVER collect, prompt for, or
store a Spotify username or password. The capture helper SHALL open a **headed**
browser (`headless=False`), and SHALL require the `browser` extra with a lazy
Playwright import and a helpful `ImportError` naming both install steps when the
extra is absent.

#### Scenario: Browser extra missing

- **WHEN** `capture_sp_dc` or `capture_sp_dc_async` is reached without Playwright installed
- **THEN** an `ImportError` is raised naming `pip install spotifyscraper[browser]` and `playwright install chromium`

#### Scenario: Cookie captured after manual login

- **WHEN** the user completes login and an `sp_dc` cookie appears on `.spotify.com`
- **THEN** `capture_sp_dc` returns the bare `sp_dc` value, captured by polling the browser context cookies (not by asserting a redirect URL)

#### Scenario: No login within the timeout

- **WHEN** no `sp_dc` cookie is captured before the timeout elapses
- **THEN** `AuthenticationError` is raised and neither the cookie nor a Playwright stack trace appears in the message

### Requirement: Persistent owner-only session store

A captured `sp_dc` SHALL be persistable to a per-user config directory as a JSON
file created with owner-only (0600) permissions, written atomically so the cookie
is never briefly world-readable. The config directory SHALL be resolved using only
the standard library, honoring `SPOTIFYSCRAPER_CONFIG_DIR`, then `XDG_CONFIG_HOME`,
then OS defaults, with NO third-party dependency. The store SHALL support reload,
and SHALL support clearing for revocation.

#### Scenario: Round-trip save and load

- **WHEN** `save_session(sp_dc)` is followed by `load_session()` against the same path
- **THEN** the loaded `Session` carries the same `sp_dc` value and its metadata

#### Scenario: Owner-only permissions on POSIX

- **WHEN** a session file is written on a POSIX system
- **THEN** its mode is 0600 and no window exists where it is group- or world-readable

#### Scenario: Config dir override precedence

- **WHEN** `SPOTIFYSCRAPER_CONFIG_DIR` is set
- **THEN** `default_config_dir()` resolves under it, ahead of `XDG_CONFIG_HOME` and the OS default

#### Scenario: Revocation

- **WHEN** `clear_session()` (or `logout()`) is called
- **THEN** the session file is removed if present and the call is idempotent when absent

### Requirement: Secrets never leak through repr, errors, logs, or fixtures

The `sp_dc` cookie value SHALL NOT appear in any `repr`, `to_dict()` is JSON-safe
and MAY include the value only as the explicit stored secret, exception messages,
log records, or committed fixtures. A `Session` `__repr__` SHALL exclude the cookie.

#### Scenario: Session repr excludes the cookie

- **WHEN** a `Session` is rendered with `repr()`
- **THEN** the output contains the metadata but never the `sp_dc` value

#### Scenario: Error messages exclude the cookie

- **WHEN** any session-store error is raised (missing, corrupt, insecure, expired)
- **THEN** the message may name the file path but never the cookie value

### Requirement: Corrupt or insecure session files are refused, not repaired

`load_session` SHALL raise a typed `SessionError` when the file is absent,
unreadable, malformed, missing `sp_dc`, or (on POSIX) group/world-readable. An
insecurely-permissioned file SHALL be REFUSED — the library SHALL NOT silently
relax or tighten permissions, because the secret may already have leaked. On
Windows, POSIX mode bits are no-ops and the per-user AppData ACL is the platform
guarantee, so the permission check SHALL be skipped there.

#### Scenario: Missing session

- **WHEN** `load_session` runs against a path with no file
- **THEN** `SessionError` is raised advising the user to log in first

#### Scenario: Malformed session

- **WHEN** the session file is not valid JSON or lacks an `sp_dc` string
- **THEN** `SessionError` is raised advising the user to log in again

#### Scenario: Insecurely-permissioned session on POSIX

- **WHEN** a POSIX session file is group- or world-readable
- **THEN** `SessionError` is raised and the file is neither loaded nor auto-chmod'd

### Requirement: Optional OS-keyring backend behind an extra

The store SHALL offer an optional keyring backend selected EXPLICITLY (never
implicitly by what is installed). The keyring backend SHALL store only the `sp_dc`
value (to stay within the Windows Credential Locker length limit), keeping
non-secret metadata in the 0600 JSON file, SHALL require a new `keyring` extra with
a lazy import and helpful `ImportError`, and SHALL fall back to the file backend
(with a warning, never a crash) when no OS keyring is available.

#### Scenario: Keyring extra missing

- **WHEN** the keyring backend is requested without `keyring` installed
- **THEN** an `ImportError` naming `spotifyscraper[keyring]` is raised

#### Scenario: Only the secret goes to the keyring

- **WHEN** a session is saved with `store="keyring"`
- **THEN** only `sp_dc` is written to the OS keyring and the metadata is written to the JSON file

#### Scenario: No OS keyring available

- **WHEN** the keyring backend is requested on a host with no Secret Service
- **THEN** the file backend is used with a warning and no exception is raised

### Requirement: Client login and saved-session entry points

`SpotifyClient`/`AsyncSpotifyClient` SHALL expose `login(...)` (opens the headed
browser once, wires the captured cookie into the client, and persists it when
`save=True`), `from_saved_session(...)` (constructs a client from a previously
saved session with no browser and no extra required to reload), and `logout(...)`
(clears the saved session). `login` SHALL reuse the existing cookie plumbing by
setting the cookie source and resetting the cached cookie-token provider, and SHALL
NOT perform any network request itself. Importing the client SHALL NOT require
Playwright; the browser import SHALL be method-level and lazy.

#### Scenario: Login wires the cookie without network I/O

- **WHEN** `login(save=False)` captures an `sp_dc` (capture stubbed)
- **THEN** the client's cookie source is set, the cached cookie-token provider is reset, and no HTTP request is made by `login` itself

#### Scenario: Reuse a saved session headlessly

- **WHEN** `from_saved_session()` runs against a previously saved session file
- **THEN** a working client is returned without launching a browser, and constructor kwargs are forwarded

#### Scenario: Saved session missing

- **WHEN** `from_saved_session()` runs with no saved session
- **THEN** `SessionError` is raised

#### Scenario: Login on a closed client

- **WHEN** `login(...)` is called after the client is closed
- **THEN** `SpotifyScraperError` is raised