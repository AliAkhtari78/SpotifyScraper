# show-extraction

## ADDED Requirements

### Requirement: Two-tier show fetch

`get_show(value)` SHALL return a `Show` via tier 1 `queryShowMetadataV2` (name, description, publisher, rating, topics, episode count) with degradation to the show's embed page (name, publisher subtitle, images).

#### Scenario: Rich fetch

- **WHEN** tier 1 succeeds for a popular show
- **THEN** the `Show` includes `publisher`, `total_episodes`, and `topics`

### Requirement: Episode listing

A tier-1 show fetch SHALL populate `show.episodes` with the first page of episodes as `Episode` values (sparse: no per-episode tier-1 fetch).

#### Scenario: Episodes present

- **WHEN** an active show is fetched via tier 1
- **THEN** `show.episodes` is non-empty and each entry has `name` and `duration_ms`
