# Design: add-cookie-auth-lyrics

**The TOTP handshake was reverse-engineered and verified live (2026-06-13).** The
exact, working algorithm is pinned below.

## auth/totp.py — the verified token-exchange algorithm

The web-player bundle (`open.spotifycdn.com/cdn/build/web-player/web-player.<hash>.js`)
contains `let eU=[{secret:'<str>',version:N},...].map(...)`, newest first. Current:

```python
# Newest first; the web player keeps a few grace versions. Refresh by re-reading
# the eU array from the current bundle (see scripts/refresh_totp.py).
TOTP_SECRETS: tuple[tuple[int, str], ...] = (
    (61, ',7/*F("rLJ2oxaKL^f+E1xvP@N'),
    (60, 'OmE{ZA.J^":0FG\\\\Uz?[@WW'),
    (59, "{iOFn;4}<1PFYKPV?5{%u14]M>/V0hDH"),
)

def _totp_key(secret: str) -> bytes:
    # Per the bundle: charCodeAt(i) XOR (i%33+9), join the decimal numbers, utf-8.
    return "".join(str(ord(c) ^ (i % 33 + 9)) for i, c in enumerate(secret)).encode()

def totp(secret: str, timestamp_s: int) -> str:
    # Standard TOTP: HMAC-SHA1, 6 digits, 30s period, counter = floor(ts/30).
    import hmac, hashlib, struct
    h = hmac.new(_totp_key(secret), struct.pack(">Q", int(timestamp_s) // 30), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return str((struct.unpack(">I", h[o : o + 4])[0] & 0x7FFFFFFF) % 1_000_000).zfill(6)
```

## auth/cookies.py — load + CookieTokenProvider

`load_sp_dc(source)`: accepts a `sp_dc` string, a mapping with `sp_dc`, or a path to
a Netscape `cookies.txt` (parse 7-tab-field lines, tolerate `#HttpOnly_` prefixes).
Missing `sp_dc` → `AuthenticationError`.

`CookieTokenProvider(transport, sp_dc, *, now_ms=...)` (+ `Async...`):
1. GET `https://open.spotify.com/api/server-time` (cookie header) → `serverTime` (s).
2. For each `(version, secret)` newest-first: build
   `https://open.spotify.com/api/token?reason=init&productType=web-player&totp=<totp(secret, now_s)>&totpServer=<totp(secret, serverTime)>&totpVer=<version>`
   with header `Cookie: sp_dc=<value>`. Parse JSON; on `isAnonymous == False` cache
   `{accessToken, accessTokenExpirationTimestampMs}` and return it. A
   `totpVerExpired` error means try the next version; all expired → `AuthenticationError`
   ("Spotify rotated its token secret; update the library / refresh TOTP_SECRETS").
   `isAnonymous == True` (or 4xx) → `AuthenticationError` with sp_dc-renewal guidance.
3. `token()` caches with a 60s expiry skew; `invalidate()` forces re-exchange.

Never log/repr the cookie or token.

## Lyrics fetch + parse (api/)

```
GET https://spclient.wg.spotify.com/color-lyrics/v2/track/<id>?format=json&vocalRemoval=false&market=from_token
Headers: Authorization: Bearer <user token>, app-platform: WebPlayer, User-Agent: <transport UA>
```

Response: `{"lyrics": {"syncType": "LINE_SYNCED"|"UNSYNCED", "provider": str, "language": str, "lines": [{"startTimeMs": str, "words": str}, ...]}}`. 404 → `NotFoundError` (track has no lyrics). 401 → invalidate token, retry once → `AuthenticationError`. `parse_lyrics(payload) -> Lyrics`: map lines to `LyricsLine(start_ms=int(startTimeMs), text=words)`, drop entries with empty `words`, carry `sync_type`/`provider`/`language`.

Note: the lyrics host `spclient.wg.spotify.com` is a distinct host (per-host rate limiting already handles it).

## Client + CLI wiring

- Constructor `cookies=` is already accepted/stored. Build the `CookieTokenProvider`
  lazily on first `get_lyrics`. `get_lyrics(value) -> Lyrics`; no cookies → immediate
  `AuthenticationError` (no network). Async mirror.
- CLI: a `lyrics` command taking a track id + `--cookies PATH`/`SPOTIFY_SP_DC` env;
  emits the lyrics `to_dict()` JSON. Update docs (lyrics now shipped).

## Testing

Unit (hermetic, respx): `_totp_key`/`totp` known-vector test (assert a fixed
timestamp+secret → expected 6-digit code, computed once and frozen); `load_sp_dc`
table; provider success (mock server-time + token), `totpVerExpired` → next-version
fallthrough, `isAnonymous:true` → AuthenticationError, caching/invalidate;
`parse_lyrics` from a synthesized payload; `get_lyrics` no-cookies → AuthenticationError
without network; 404 → NotFoundError. Live (`@pytest.mark.live`, skipif no
`SPOTIFY_SP_DC`): real `get_lyrics("4uLU6hMCjMI75M1A2tKUQC")` returns LINE_SYNCED
lines.
