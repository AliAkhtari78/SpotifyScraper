# command-line-interface

## ADDED Requirements

### Requirement: Entity commands emit JSON

The CLI SHALL provide a command for each entity type — `track`, `album`,
`artist`, `playlist`, `episode`, `show` — that accepts a Spotify URL, URI, or ID
and writes the entity's `to_dict()` as JSON to stdout. `--pretty` SHALL produce
indented JSON; `-o/--output PATH` SHALL write to a file instead of stdout.

#### Scenario: Track as JSON

- **WHEN** `spotifyscraper track <id>` runs successfully
- **THEN** stdout is a single valid JSON object containing the track's `name`
  and `id`, and the exit code is 0

#### Scenario: Pretty output

- **WHEN** `--pretty` is passed
- **THEN** the JSON is indented and human-readable

### Requirement: Media download commands

The CLI SHALL provide a `download` command group with `cover` and `preview`
subcommands that accept a track (or, for cover, any entity) URL/URI/ID, fetch the
entity, download the asset to a destination directory (`-o/--output`, default
`.`), and print the written path. `download preview --embed-cover` SHALL embed
the cover (requiring the `media` extra).

#### Scenario: Download a preview

- **WHEN** `spotifyscraper download preview <track-id> -o out/` runs
- **THEN** an MP3 is written under `out/` and its path is printed, exit code 0

### Requirement: Pagination and tuning options

`playlist` SHALL accept `--max-tracks` (default 100; `0` or `all` meaning every
track) and `show` SHALL accept `--max-episodes`. All commands SHALL accept
`--proxy`, `--timeout`, and `--rate-limit` (requests/second) to configure the
client.

#### Scenario: Bounded playlist

- **WHEN** `spotifyscraper playlist <id> --max-tracks 50` runs
- **THEN** at most 50 tracks appear in the output

### Requirement: Clean error handling and exit codes

Library exceptions SHALL be caught and reported as a concise `error: <message>`
on stderr with a non-zero exit code — never a raw Python traceback. `NotFoundError`
SHALL map to exit code 3, `AuthenticationError` to 4, and other
`SpotifyScraperError`s to 1.

#### Scenario: Missing entity

- **WHEN** a command targets a non-existent entity
- **THEN** stderr shows `error: ...`, stdout is empty, and the exit code is 3

### Requirement: Discoverability

The CLI SHALL provide `--help` for the app and every command, and `--version`
SHALL print the package version.

#### Scenario: Version

- **WHEN** `spotifyscraper --version` runs
- **THEN** it prints the installed version and exits 0
