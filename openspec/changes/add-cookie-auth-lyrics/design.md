# Design: add-cookie-auth-lyrics

## auth/cookies.py

```python
def load_sp_dc(source: str | Path | Mapping[str, str]) -> str
    # Mapping: source["sp_dc"]; str/Path: if os.path-like exists -> parse Netscape cookies.txt
    # (tab-separated 7 fields, skip comments; also tolerate '#HttpOnly_' prefixes);
    # plain str that looks like a cookie value (no path separators, len>20) -> treated as sp_dc itself.
    # Missing sp_dc -> AuthenticationError.

TOKEN_URL = "https://open.spotify.com/api/token?reason=init&productType=web-player"
# NOTE: Spotify has moved this endpoint before (formerly /get_access_token). Validate live during
# implementation with a real sp_dc; if a TOTP/server-time handshake is now required, implement the
# documented handshake in _exchange() and record the final shape here before archiving this change.

class CookieTokenProvider:
    def __init__(self, transport: Transport, sp_dc: str, *, now_ms=...) -> None
    def token(self) -> str        # cached; refresh on expiry skew (60s) or invalidate()
    def invalidate(self) -> None
class AsyncCookieTokenProvider:   # mirror
```

Exchange: GET TOKEN_URL with `Cookie: sp_dc=<value>` → JSON `{accessToken, accessTokenExpirationTimestampMs, isAnonymous}`. `isAnonymous: true` in the response means the cookie was rejected → `AuthenticationError` with renewal instructions.

## Lyrics endpoint

```
GET https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}?format=json&vocalRemoval=false&market=from_token
Headers: Authorization: Bearer <cookie token>, App-Platform: WebPlayer, User-Agent: <transport UA>
```

Response: `lyrics.lines[] {startTimeMs (str), words (str)}`, `lyrics.syncType`, `lyrics.provider`, `lyrics.language`. 404 → `NotFoundError`; 401 → invalidate + retry once → `AuthenticationError`.

Parser `parse_lyrics(payload) -> Lyrics` in `api/parse_entities.py` (pure): skip empty `words` markers ("♪" kept, "" dropped), startTimeMs str→int.

## Client wiring

- Constructor: `cookies` param (already accepted) now builds `CookieTokenProvider` lazily at first `get_lyrics` call (construction validates `sp_dc` presence only — fast fail without network).
- `get_lyrics(value: str) -> Lyrics`; async mirror.

## Testing

Unit: load_sp_dc table (cookies.txt with/without sp_dc, HttpOnly prefix, dict, raw value); provider caching/refresh/invalidate with fake transport; isAnonymous-true → AuthenticationError; parse_lyrics fixture (synthesized from documented shape — no real payload committed); 404→NotFoundError vs 401→AuthenticationError classification; credential-hygiene asserts (no sp_dc text in raised messages). Live (skipif no `SPOTIFY_SP_DC` env): exchange + fetch lyrics for the canonical track, assert non-empty lines.
