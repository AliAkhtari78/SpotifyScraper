# canary-monitoring

## ADDED Requirements

### Requirement: Daily live verification

A scheduled workflow SHALL run the live test suite (`pytest -m live`) daily against real Spotify endpoints, and on demand via manual dispatch.

#### Scenario: Healthy day

- **WHEN** the canary passes
- **THEN** no issue is opened and any open `spotify-breakage` issue gets a "recovered" comment and is closed

### Requirement: Automated breakage reporting

On canary failure, the workflow SHALL create — or update, if open — a single pinned issue labeled `spotify-breakage` containing the failing test names and a link to the run. Repeated failures SHALL NOT create duplicate issues.

#### Scenario: Spotify changes a payload

- **WHEN** the canary fails two days in a row
- **THEN** exactly one `spotify-breakage` issue exists, updated with both runs

### Requirement: Lyrics canary is non-blocking

Lyrics live tests (requiring the `SPOTIFY_SP_DC` secret) SHALL be skipped when the secret is absent and SHALL NOT fail the canary when only lyrics tests fail (separate job or `continue-on-error`).

#### Scenario: Expired maintainer cookie

- **WHEN** only the lyrics live test fails
- **THEN** the canary reports success for core extraction and flags lyrics separately
