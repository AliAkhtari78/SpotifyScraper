# Lyrics & cookies

Lyrics and podcast transcripts are **logged-in-only** Spotify features. Unlike
every other extractor in SpotifyScraper, `get_lyrics` and `get_transcript` need
an authenticated `sp_dc` cookie from your own Spotify account. This guide shows
how to obtain that cookie, how to feed it to the client, and the security
trade-offs you are accepting. The same cookie powers both — a single client
exchanges it once and reuses the token for lyrics and transcripts alike.

!!! warning "Your `sp_dc` cookie is a credential"
    An `sp_dc` cookie is roughly equivalent to a login session for your Spotify
    account. **Treat it like a password.** Never commit it to source control,
    paste it into issues, or share it. SpotifyScraper never logs or prints it,
    and it never appears in exception messages — but you are responsible for how
    you store it. Use it only with your own account and at your own risk; this
    is for personal, educational, and research use.

## Getting your `sp_dc` cookie

1. Open <https://open.spotify.com> in a desktop browser and **log in**.
2. Open your browser's developer tools (F12 or right-click → Inspect).
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
4. Under **Cookies → `https://open.spotify.com`**, find the row named **`sp_dc`**.
5. Copy its **Value** — a long opaque string. That value is your `sp_dc` cookie.

You can pass that value directly, or export a Netscape-format `cookies.txt`
(many browser extensions do this) and point the client at the file.

## Python usage

`SpotifyClient` accepts cookies three ways via the `cookies=` argument: a raw
`sp_dc` string, a mapping containing an `sp_dc` key, or a path to a
`cookies.txt` file.

```python
from spotify_scraper import SpotifyClient

# 1) A raw sp_dc string
with SpotifyClient(cookies="AQ...your_sp_dc...") as client:
    lyrics = client.get_lyrics("4uLU6hMCjMI75M1A2tKUQC")

# 2) A cookies.txt export
with SpotifyClient(cookies="cookies.txt") as client:
    lyrics = client.get_lyrics("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC")

# 3) A mapping
with SpotifyClient(cookies={"sp_dc": "AQ..."}) as client:
    lyrics = client.get_lyrics("spotify:track:4uLU6hMCjMI75M1A2tKUQC")

print(lyrics.sync_type)  # "LINE_SYNCED" or "UNSYNCED"
for line in lyrics.lines:
    print(line.start_ms, line.text)
```

`get_lyrics` accepts a track URL, URI, or bare 22-character ID — exactly like
`get_track`. The returned [`Lyrics`](../reference/models.md) model carries the
synchronized `lines` (each a `LyricsLine` with a `start_ms` offset and `text`),
the `sync_type`, and the `provider`/`language` when Spotify supplies them.

The async client mirrors the API:

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient(cookies="cookies.txt") as client:
    lyrics = await client.get_lyrics("4uLU6hMCjMI75M1A2tKUQC")
```

## Command-line usage

The `spotifyscraper lyrics` command takes a track and a cookie source. Pass
`--cookies PATH`, or set the `SPOTIFY_SP_DC` environment variable to your raw
`sp_dc` value:

```bash
# Via a cookies.txt file
spotifyscraper lyrics 4uLU6hMCjMI75M1A2tKUQC --cookies cookies.txt --pretty

# Via the environment variable (keeps the secret out of your shell history)
export SPOTIFY_SP_DC="AQ...your_sp_dc..."
spotifyscraper lyrics 4uLU6hMCjMI75M1A2tKUQC -o lyrics.json
```

The command emits the lyrics `to_dict()` JSON to stdout (or to `-o FILE`), with
`--pretty` for indented output.

## Podcast transcripts

`get_transcript` reads a podcast **episode's** transcript through the same
cookie-authenticated handshake. It takes an episode URL, URI, or bare ID and
returns a [`Transcript`](../reference/models.md) whose `lines` are
`TranscriptLine` entries — each with a millisecond `start_ms` offset and `text`:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient(cookies="cookies.txt") as client:
    transcript = client.get_transcript("https://open.spotify.com/episode/512ojhOuo1ktJprKbVcKyQ")
    print(transcript.language)
    for line in transcript.lines:
        print(line.start_ms, line.text)
```

The async client mirrors it: `await client.get_transcript(episode_id)`.

Not every episode is transcribed. When an episode has no transcript — whether
Spotify 404s or returns a body with no spoken text — `get_transcript` raises
`NotFoundError` (never confused with an auth failure). On the command line:

```bash
spotifyscraper transcript 512ojhOuo1ktJprKbVcKyQ --cookies cookies.txt --pretty
```

## Errors you may hit

| Situation | Exception | CLI exit code |
|---|---|---|
| No cookies configured | `AuthenticationError` (raised immediately, no network) | 4 |
| Expired or invalid `sp_dc` | `AuthenticationError` with renewal instructions | 4 |
| Track exists but has no lyrics | `NotFoundError` | 3 |
| Episode has no transcript | `NotFoundError` | 3 |

If you see an `AuthenticationError` telling you to refresh your cookie, log back
into open.spotify.com and re-export `sp_dc` — sessions expire. A `NotFoundError`
means the track simply has no lyrics (e.g. instrumentals); it is never confused
with an authentication failure.

!!! note "Token-secret rotation"
    The cookie-to-token handshake relies on a TOTP secret that Spotify rotates
    periodically. SpotifyScraper ships the current secrets and tries the newest
    first. If every version is rejected you will get an `AuthenticationError`
    asking you to update the library — upgrade to the latest release.
