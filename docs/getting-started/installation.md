# Installation

SpotifyScraper requires **Python 3.10 or newer** and has a single runtime
dependency: [`httpx`](https://www.python-httpx.org/). Everything else is an
optional extra you opt into only when you need it.

## Install the core library

=== "pip"

    ```bash
    pip install spotifyscraper
    ```

=== "uv"

    ```bash
    uv add spotifyscraper
    ```

That is all you need to fetch tracks, albums, artists, playlists, episodes, and
shows, and to download raw cover art and preview clips.

## Extras

Extras pull in optional dependencies behind lazy imports — installing the core
library keeps your environment lean, and you add capabilities as needed.

| Extra | Adds | Install |
|---|---|---|
| `media` | [`mutagen`](https://mutagen.readthedocs.io/) for embedding cover art and ID3 tags into downloaded previews | `pip install "spotifyscraper[media]"` |
| `browser` | [`playwright`](https://playwright.dev/python/) Chromium transport and browser-assisted `login()` | `pip install "spotifyscraper[browser]"` |
| `cli` | [`typer`](https://typer.tiangolo.com/) for the `spotifyscraper` command-line tool | `pip install "spotifyscraper[cli]"` |
| `keyring` | [`keyring`](https://pypi.org/project/keyring/) to store the login cookie in the OS keyring | `pip install "spotifyscraper[keyring]"` |
| `mcp` | the `spotifyscraper-mcp` [Model Context Protocol](https://modelcontextprotocol.io) server for LLM hosts | `pip install "spotifyscraper[mcp]"` |
| `all` | Everything above | `pip install "spotifyscraper[all]"` |

=== "pip"

    ```bash
    pip install "spotifyscraper[media]"
    pip install "spotifyscraper[cli]"
    pip install "spotifyscraper[mcp]"
    pip install "spotifyscraper[all]"
    ```

=== "uv"

    ```bash
    uv add "spotifyscraper[media]"
    uv add "spotifyscraper[cli]"
    uv add "spotifyscraper[mcp]"
    uv add "spotifyscraper[all]"
    ```

!!! tip "Quote the extras"
    Some shells (notably `zsh`) treat square brackets as glob patterns. Wrap the
    package spec in quotes — `"spotifyscraper[media]"` — to be safe.

## Browser fallback: install Chromium

The `browser` extra installs the Playwright *Python* package, but Playwright
also needs a browser binary. After installing the extra, download Chromium once:

```bash
pip install "spotifyscraper[browser]"
playwright install chromium
```

If you skip `playwright install chromium`, importing the browser transport still
works, but the first request raises a Playwright error telling you to install the
browser. See the [Browser fallback guide](../guides/browser-fallback.md) for when
and how to use it.

## Supported Python versions

| Version | Supported |
|---|---|
| 3.10 | :material-check: |
| 3.11 | :material-check: |
| 3.12 | :material-check: |
| 3.13 | :material-check: |

Older interpreters are not supported.

## Verify your install

```python
import spotify_scraper

print(spotify_scraper.__version__)
```

Then continue to the [Quickstart](quickstart.md).
