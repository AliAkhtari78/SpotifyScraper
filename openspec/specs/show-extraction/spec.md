# show-extraction Specification

## Purpose
TBD - created by archiving change add-podcast-entities. Update Purpose after archive.
## Requirements
### Requirement: Two-tier show fetch

`get_show(value)` SHALL return a `Show` via tier 1 `queryShowMetadataV2` (name, description, publisher, rating, topics) with degradation to the show's embed page (name, publisher subtitle, images).

#### Scenario: Rich fetch

- **WHEN** tier 1 succeeds for a popular show
- **THEN** the `Show` includes `publisher` and `topics`

### Requirement: Metadata operation carries no episode listing

The `queryShowMetadataV2` operation used by this capability SHALL NOT be relied upon for a full episode listing or a reliable episode count (its `episodesV2` block lacks `totalCount` and carries at most a uri-only stub). The complete, paginated episode listing SHALL be specified separately by the `show-episodes` capability, which `get_show` uses to populate `total_episodes` and `episodes`.

#### Scenario: Metadata alone

- **WHEN** only the `queryShowMetadataV2` response is parsed (no episode-listing pass)
- **THEN** `total_episodes` is `None` and `episodes` is empty, without error

