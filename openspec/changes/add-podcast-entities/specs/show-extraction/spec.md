# show-extraction

## ADDED Requirements

### Requirement: Two-tier show fetch

`get_show(value)` SHALL return a `Show` via tier 1 `queryShowMetadataV2` (name, description, publisher, rating, topics) with degradation to the show's embed page (name, publisher subtitle, images).

#### Scenario: Rich fetch

- **WHEN** tier 1 succeeds for a popular show
- **THEN** the `Show` includes `publisher` and `topics`

### Requirement: Episode count and listing are best-effort

The `queryShowMetadataV2` operation does not return a full episode listing or a reliable episode count: it carries an `episodesV2` block without `totalCount` and with at most a single uri-only episode stub. `get_show` SHALL therefore populate `total_episodes` and `episodes` only when the payload actually provides them, leaving `total_episodes` as `None` and `episodes` empty otherwise — without raising. A complete, paginated episode listing is out of scope for v3.0.0 (it would require a separate podcast-episodes operation) and is a candidate for a later minor release.

#### Scenario: Count present in payload

- **WHEN** a show payload includes `episodesV2.totalCount`
- **THEN** `show.total_episodes` equals that count

#### Scenario: Count absent in payload

- **WHEN** a show payload omits `episodesV2.totalCount` (the common case today)
- **THEN** `show.total_episodes` is `None`, `show.episodes` is empty, and no error is raised
