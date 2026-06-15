# Authenticated sessions

Some Spotify data — lyrics, podcast transcripts — is only available to a
**logged-in** account. Rather than ask for your password (Spotify gates login
behind bot detection, CAPTCHAs, and 2FA, and a stored password is a liability),
SpotifyScraper captures the `sp_dc` session cookie from a **real browser you log
into by hand**, then persists it so later runs are headless.

!!! warning "Your `sp_dc` cookie is a credential"
    A captured `sp_dc` cookie is roughly a login session for your account.
    **Treat it like a password.** SpotifyScraper never logs or prints it, stores
    it in an owner-only (0600) file, and keeps it out of every `repr` and
    exception message — but you are responsible for the machine it lives on. Use
    it only with your own account.

## Browser-assisted login

`client.login()` opens a **headed** Chromium window at the Spotify login page.
You sign in by hand; the library polls the browser's cookies until `sp_dc`
appears, wires it into the client, and (by default) saves it for reuse:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    client.login()                      # opens a real browser; you log in
    lyrics = client.get_lyrics("4uLU6hMCjMI75M1A2tKUQC")
```

`login()` needs the **`browser`** extra and a real display, so it is a
desktop/interactive step:

```bash
pip install "spotifyscraper[browser]"
playwright install chromium
```

Without the extra, `login()` raises a clear `ImportError` naming both install
steps. No username or password is ever collected — only the resulting cookie.
When you close the window, **do not click "Log out"** (that invalidates the
cookie you just captured).

By default `login(reuse=True)` **skips the browser when a valid saved session
already exists** — so the same `login()` call is safe to run repeatedly, opening
a browser only the first time (or after the session expires). Pass `reuse=False`
to force a fresh capture. The validity check is local (file present, securely
permissioned, parses, not past its known expiry, and — for the keyring backend —
the secret is still retrievable), so reuse never makes a network call.

The async client mirrors it: `await client.login()`.

## Reusing a saved session (headless)

Once a session is saved, reconnect later with **no browser** — ideal for
servers and cron jobs:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient.from_saved_session() as client:
    transcript = client.get_transcript("512ojhOuo1ktJprKbVcKyQ")
```

`from_saved_session()` reads the saved cookie and forwards any client kwargs
(`proxy`, `timeout`, `rate_limit`, …). If no usable session exists it raises
`SessionError`. Browser-captured sessions also record the cookie's **real
expiry**, so tooling can tell you how long the session is good for.

## Where the cookie is stored

The session lives in a per-user config directory (overridable with
`SPOTIFYSCRAPER_CONFIG_DIR`, then `XDG_CONFIG_HOME`, then the OS default). Two
backends are available, and the choice is always **explicit** — never inferred
from what happens to be installed:

| `store=` | Where the secret lives | Needs |
|---|---|---|
| `"file"` (default) | An owner-only (0600) JSON file | nothing |
| `"keyring"` | The OS keyring (Keychain / Credential Locker / Secret Service); only metadata in the file | the `keyring` extra |

```python
client.login(store="keyring")                       # secret -> OS keyring
client = SpotifyClient.from_saved_session(store="keyring")
```

```bash
pip install "spotifyscraper[keyring]"
```

Requesting `store="keyring"` without the extra raises an `ImportError` naming
`spotifyscraper[keyring]`. On a host with no usable keyring (e.g. a headless
Linux box with no Secret Service), the keyring backend falls back to the file
backend with a warning rather than crashing.

## Revoking a saved session

`logout()` (or `clear_session()`) removes the saved session locally; it is
idempotent when nothing is saved:

```python
SpotifyClient.logout()                  # or logout(store="keyring")
```

This only deletes the **local** copy. To revoke the cookie everywhere, change
your Spotify password, which invalidates existing `sp_dc` cookies.

## Inspecting the saved session

`SpotifyClient.session_info()` reports a saved session's status **without
exposing the cookie** — useful for a health check before a headless run. It
returns a cookie-free [`SessionInfo`](../reference/models.md) (`exists`, `valid`,
`saved_at_ms`, `sp_dc_expires_ms`, `reason`, plus a JSON-safe `to_dict()`) and
never raises for a missing, corrupt, insecure, or expired session:

```python
info = SpotifyClient.session_info()         # or session_info(store="keyring")
if not info.valid:
    print("Need to log in:", info.reason)
```

::: spotify_scraper.auth.session.SessionInfo

## Knowing your account

With a session, `get_account()` returns the logged-in account's product state —
tier, country, and locale — and `is_premium()` is a convenience for the common
check:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient.from_saved_session() as client:
    account = client.get_account()
    print(account.product, account.country)     # e.g. "premium" CA
    if client.is_premium():
        ...
```

`get_account()` needs cookies (it raises `AuthenticationError` immediately
otherwise) and takes no argument — the product-state body is a flat per-account
object. The derived `is_premium` is a property, so it is excluded from
`Account.to_dict()` (which mirrors the wire body).

## Command line

```bash
spotifyscraper login                    # reuse a valid session, else open the browser
spotifyscraper login --no-reuse         # force a fresh browser capture
spotifyscraper login --store keyring    # store the secret in the OS keyring
spotifyscraper session                  # print the saved session's status (no cookie)
spotifyscraper logout                   # clear the saved session
```

Only paths and cookie-free status are printed — never the cookie.
