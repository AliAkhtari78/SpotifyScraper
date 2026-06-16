# episode-extraction Specification

## Purpose
TBD - created by archiving change add-podcast-entities. Update Purpose after archive.
## Requirements
### Requirement: Two-tier episode fetch

`get_episode(value)` SHALL return an `Episode` via tier 1 `getEpisodeOrChapter` (name, descriptions, duration, release date, cover art, show reference, preview audio) with degradation to the episode's embed page (name, duration, release date, preview audio, images).

#### Scenario: Issue #88 regression

- **WHEN** a current podcast episode is fetched live
- **THEN** an `Episode` with non-empty `name`, positive `duration_ms`, and a `show` reference is returned (the v2 failure mode reported in issue #88 does not occur)

#### Scenario: Degraded fetch

- **WHEN** tier 1 fails with `ParsingError`
- **THEN** an embed-built `Episode` is returned with `show` possibly `None`

