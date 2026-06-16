# embed-parsing

## ADDED Requirements

### Requirement: NEXT_DATA extraction

The library SHALL extract the `__NEXT_DATA__` JSON script payload from embed-page HTML and raise `ParsingError` when it is absent or malformed.

#### Scenario: Valid embed page

- **WHEN** a captured embed fixture is parsed
- **THEN** a JSON object with `props.pageProps.state` is returned

### Requirement: Entity payload access

The library SHALL expose the embedded entity data (`props.pageProps.state.data.entity`) and raise `NotFoundError` when the page reports a missing or unavailable entity (status/forbiddenReason markers instead of entity data).

#### Scenario: Dead entity

- **WHEN** an embed payload contains an error status instead of an entity block
- **THEN** `NotFoundError` is raised

### Requirement: Session payload access

The library SHALL expose the session block (access token, expiry timestamp, anonymity flag) from any entity's embed payload.

#### Scenario: Session from any entity type

- **WHEN** the session block is read from each of the six captured entity fixtures
- **THEN** every payload yields a token and expiry
