# mcp Specification

## Purpose

A Model Context Protocol server exposing the library as tools, resources, and prompts.

## Requirements
### Requirement: Model Context Protocol server

The optional `mcp` extra SHALL provide a `spotifyscraper-mcp` server that exposes
every public getter as a tool returning JSON-safe structured output, the six
entity types as `spotify://{type}/{id}` resources, curated prompts, and both
stdio and streamable-HTTP transports. Authenticated tools MUST return a clean
error (naming `SPOTIFY_SP_DC`) when no cookie is configured, and MUST NOT log the
cookie or any token.

#### Scenario: Authenticated tool without a cookie

- **WHEN** an authenticated tool (e.g. `get_credits`) is called on a server
  started without `SPOTIFY_SP_DC`
- **THEN** the tool returns an error that names `SPOTIFY_SP_DC`, touches no
  network, and logs no secret

#### Scenario: Anonymous tool succeeds

- **WHEN** `get_track` is called through the in-memory MCP session
- **THEN** the tool returns the track as structured JSON output

### Requirement: Batch getter tools

The MCP server SHALL expose the library's plural getters as tools — `get_tracks`,
`get_albums`, `get_artists`, `get_playlists`, `get_episodes`, and `get_shows` —
each accepting a list of URLs/URIs/IDs and returning one ordered item per input
with the shape `{value, ok, result, error}`: the model's JSON-safe `to_dict()` on
success (with `error` null), or the captured error message on failure (with
`result` null). A single failing input SHALL NOT fail the whole call.
`get_playlists` and `get_shows` SHALL accept `max_tracks` / `max_episodes`.

#### Scenario: Mixed batch

- **WHEN** `get_tracks` is called with one valid and one invalid id
- **THEN** the call succeeds and returns two ordered items — the valid one with
  `ok` true and a `result`, the invalid one with `ok` false and a non-empty `error`

### Requirement: One-call track visuals tool

The MCP server SHALL expose a `get_track_visuals` tool returning a track with its
cover `colors` and `canvas` in one response. `track` and `colors` SHALL always be
present (anonymous); `canvas` SHALL be best-effort — the Canvas video when a
cookie is configured and the track has one, else null — and a missing cookie or
absent Canvas SHALL NOT fail the call.

#### Scenario: Visuals without a cookie

- **WHEN** `get_track_visuals` is called on a server started without `SPOTIFY_SP_DC`
- **THEN** the response includes the track and its colors, and `canvas` is null

