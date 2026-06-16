# mcp Specification

## Purpose
TBD - created by archiving change add-visual-discovery-mcp. Update Purpose after archive.
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

