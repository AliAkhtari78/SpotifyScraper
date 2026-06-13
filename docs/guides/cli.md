# Command-line interface

SpotifyScraper ships a `spotifyscraper` command that prints any entity as JSON
and downloads cover art or preview clips — handy for shell pipelines, quick
lookups, and feeding `jq`.

## Install

The CLI lives behind the `cli` extra (it pulls in [Typer](https://typer.tiangolo.com/)):

```bash
pip install "spotifyscraper[cli]"
```

Want media tagging too (for `download preview --embed-cover`)? Add the `media`
extra:

```bash
pip install "spotifyscraper[cli,media]"
```

Verify the install:

```bash
spotifyscraper --version
spotifyscraper --help
```

## Entity commands

Each entity type has a command that accepts a Spotify **URL**, **URI**, or bare
**22-character ID** and writes the entity's `to_dict()` as JSON to stdout:

| Command | Fetches |
|---|---|
| `spotifyscraper track <id>` | a `Track` |
| `spotifyscraper album <id>` | an `Album` with its tracks |
| `spotifyscraper artist <id>` | an `Artist` |
| `spotifyscraper playlist <id>` | a `Playlist` |
| `spotifyscraper episode <id>` | an `Episode` |
| `spotifyscraper show <id>` | a `Show` with its episodes |

```bash
spotifyscraper track 4uLU6hMCjMI75M1A2tKUQC
spotifyscraper album "https://open.spotify.com/album/..."
spotifyscraper artist spotify:artist:0gxyHStUsqpMadRV0Di1Qt
```

### Pretty printing and files

By default the JSON is compact (one line). Use `--pretty` for indented,
human-readable output, and `-o/--output PATH` to write to a file instead of
stdout:

```bash
spotifyscraper track 4uLU6hMCjMI75M1A2tKUQC --pretty
spotifyscraper album <id> -o album.json
```

### Piping to `jq`

Compact JSON pipes straight into [`jq`](https://jqlang.github.io/jq/):

```bash
# Just the track name
spotifyscraper track 4uLU6hMCjMI75M1A2tKUQC | jq -r '.name'

# Every artist on an album
spotifyscraper album <id> | jq -r '.artists[].name'

# Title + duration for each playlist track
spotifyscraper playlist <id> | jq -r '.tracks[].track | "\(.name) (\(.duration_ms)ms)"'
```

## Pagination

`playlist` accepts `--max-tracks` and `show` accepts `--max-episodes`. Pass an
integer to cap the count, or `all` (or `0`) to fetch everything:

```bash
spotifyscraper playlist <id> --max-tracks 50      # at most 50 tracks
spotifyscraper playlist <id> --max-tracks all     # every track
spotifyscraper show <id> --max-episodes 10        # at most 10 episodes
spotifyscraper show <id> --max-episodes all       # every episode
```

`--max-tracks` defaults to `100` and `--max-episodes` defaults to `50`.

## Tuning the client

Every command takes the same client knobs:

| Option | Effect |
|---|---|
| `--proxy URL` | Route requests through a proxy. |
| `--timeout SECONDS` | Per-request timeout (default `10`). |
| `--rate-limit N` | Sustained requests per second (maps to `RateLimit(per_second=N)`). |

```bash
spotifyscraper playlist <id> --rate-limit 1 --timeout 20 --proxy http://127.0.0.1:8080
```

See [Anti-ban & resilience](anti-ban.md) for guidance on choosing a rate.

## Downloads

The `download` group writes media to a directory and prints the written path.

### Cover art

```bash
spotifyscraper download cover <track-id> -o covers/
spotifyscraper download cover <track-id> --size smallest --name cover
```

| Option | Effect |
|---|---|
| `-o/--output DIR` | Destination directory (default `.`, created if missing). |
| `--size largest\|smallest` | Pick the largest (default) or smallest available image. |
| `--name NAME` | Explicit filename; defaults to a sanitized entity name. |

### Preview clips

```bash
spotifyscraper download preview <track-id> -o previews/
spotifyscraper download preview <track-id> --embed-cover   # needs the media extra
```

| Option | Effect |
|---|---|
| `-o/--output DIR` | Destination directory (default `.`, created if missing). |
| `--embed-cover` | Embed cover art and ID3 tags (requires `spotifyscraper[media]`). |
| `--name NAME` | Explicit filename; defaults to a sanitized entity name. |

Previews are the ~30-second clips Spotify publishes publicly. Full-song
downloads are not supported — see [Media downloads](media-downloads.md).

## Exit codes

Library errors are reported as a concise `error: <message>` on **stderr** (never
a raw traceback) with a non-zero exit code:

| Exit code | Meaning |
|---|---|
| `0` | Success. |
| `1` | A general `SpotifyScraperError`. |
| `3` | `NotFoundError` — the entity does not exist. |
| `4` | `AuthenticationError` — missing or expired credentials. |

```bash
spotifyscraper track does-not-exist
# stderr: error: ...
echo $?   # 3
```

This makes the CLI safe to use in scripts with `set -e`.

## Lyrics

The `lyrics` command fetches time-synced lyrics (cookie-authenticated):

```bash
spotifyscraper lyrics 4uLU6hMCjMI75M1A2tKUQC --cookies cookies.txt
# or: export SPOTIFY_SP_DC=... && spotifyscraper lyrics <id>
```

See the [lyrics & cookies guide](lyrics-and-cookies.md) for how to obtain your
`sp_dc` cookie.
