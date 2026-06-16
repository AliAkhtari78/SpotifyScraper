# data-models Specification

## Purpose
TBD - created by archiving change add-models-errors-urls. Update Purpose after archive.
## Requirements
### Requirement: Immutable typed models

Entity models (`Track`, `Album`, `Artist`, `Playlist`, `Episode`, `Show`, `Lyrics`) and value objects (`Image`, `ArtistRef`, `AlbumRef`, `ShowRef`, `UserRef`, `PlaylistTrack`, `LyricsLine`) SHALL be frozen, slotted dataclasses with full type annotations passing `mypy --strict`.

#### Scenario: Mutation attempt

- **WHEN** code assigns to a field of a constructed model
- **THEN** `dataclasses.FrozenInstanceError` is raised

### Requirement: Two-tier nullability contract

Fields obtainable from the embed page (tier 2) SHALL be non-optional; fields only obtainable from the pathfinder API (tier 1) SHALL be typed `| None` and default to `None`.

#### Scenario: Track built from embed data only

- **WHEN** a `Track` is constructed from an embed payload (no tier-1 data)
- **THEN** construction succeeds, with tier-1-only fields (e.g. `play_count`, `track_number`) set to `None`

### Requirement: JSON-safe serialization round-trip

Every model SHALL provide `to_dict()` returning only JSON-serializable primitives (datetimes become ISO-8601 strings) and a `from_dict()` classmethod such that `Model.from_dict(m.to_dict())` equals `m`.

#### Scenario: Round trip

- **WHEN** any fully-populated model is serialized with `to_dict()` and rebuilt with `from_dict()`
- **THEN** the rebuilt instance equals the original

#### Scenario: JSON dump

- **WHEN** `json.dumps(model.to_dict())` is called
- **THEN** it succeeds without a custom encoder

