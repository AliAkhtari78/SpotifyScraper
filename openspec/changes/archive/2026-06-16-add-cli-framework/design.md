# Design: add-cli-framework

## Packaging

```toml
[project.optional-dependencies]
cli = ["typer>=0.12"]

[project.scripts]
spotifyscraper = "spotify_scraper.cli:app"
```

`typer` pulls in `click` + `rich` (for help formatting). Add `typer` to the dev
dependency group so the CLI tests run by default. Keep the `cli` import lazy at
the package root so `import spotify_scraper` never requires typer.

## Module layout

```
src/spotify_scraper/cli/
├── __init__.py        # `app` (typer.Typer); raises a helpful error if typer missing
├── main.py            # the Typer app, global callback (--version), entity commands
├── download.py        # the `download` sub-app (cover, preview)
└── _output.py         # JSON rendering (to_dict -> json), file/stdout, error mapping
```

`spotify_scraper.cli:app` is the entry point. `cli/__init__.py` does
`from spotify_scraper.cli.main import app` inside a try/except ImportError that
re-raises with `pip install "spotifyscraper[cli]"`.

## Commands

Global callback: `--version` (eager), and shared client options collected into a
small helper `build_client(proxy, timeout, rate_limit) -> SpotifyClient`.

| Command | Args / options | Output |
|---|---|---|
| `track ID` | `--pretty`, `-o` | `Track.to_dict()` JSON |
| `album ID` | `--pretty`, `-o` | `Album.to_dict()` |
| `artist ID` | `--pretty`, `-o` | `Artist.to_dict()` |
| `playlist ID` | `--max-tracks` (int/"all"), `--pretty`, `-o` | `Playlist.to_dict()` |
| `episode ID` | `--pretty`, `-o` | `Episode.to_dict()` |
| `show ID` | `--max-episodes`, `--pretty`, `-o` | `Show.to_dict()` |
| `download cover ID` | `-o DIR`, `--size`, `--name` | prints written path |
| `download preview ID` | `-o DIR`, `--embed-cover`, `--name` | prints written path |

Shared options (`--proxy`, `--timeout`, `--rate-limit`) live on each command (or
the group) and feed `build_client`. `--rate-limit` maps to `RateLimit(per_second=...)`.

`--max-tracks all` / `0` → `None` (fetch everything).

## Output and errors (`_output.py`)

- `emit(data: Mapping, *, pretty: bool, output: Path | None)`: `json.dumps`
  (indent=2 if pretty), write to file or stdout (+ trailing newline).
- `run(fn)`: wraps a command body, catches `SpotifyScraperError` subtypes and
  calls `typer.echo(f"error: {exc}", err=True); raise typer.Exit(code)` with the
  spec's exit-code map (NotFound→3, Authentication→4, else→1). Keeps tracebacks
  out of the UX.

## Testing

`tests/unit/cli/` using `typer.testing.CliRunner` with the client mocked
(monkeypatch `spotify_scraper.cli.main.SpotifyClient` to a fake returning fixture
models, or respx on the transport): JSON shape per command, `--pretty`, `-o`
file write, `--max-tracks`/`--max-episodes` plumbing, error mapping + exit codes,
`--version`, `--help`. A `@pytest.mark.live` smoke runs the real `track` command.

## Docs

`docs/guides/cli.md` (added to nav) with install (`[cli]` extra), every command,
examples (piping JSON to `jq`), and the download commands. Update `index.md`/FAQ
to note the CLI now exists (remove "coming in v3.1" for the CLI).

## Out of scope

The `lyrics` command ships with cookie-auth lyrics support (separate change).
