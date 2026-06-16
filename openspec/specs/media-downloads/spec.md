# media-downloads Specification

## Purpose
TBD - created by archiving change add-media-downloads. Update Purpose after archive.
## Requirements
### Requirement: Cover art download

`download_cover(entity, dest=".", *, size="largest", filename=None)` SHALL accept any entity model with images, pick the requested size (`"largest"`, `"smallest"`), download it through the client's transport, and return the written `Path`. Filenames default to a sanitized `<entity name>.<ext>` (extension from the response content type, default `jpg`).

#### Scenario: Track cover

- **WHEN** a track's cover is downloaded to a temp directory
- **THEN** a readable image file named after the track exists at the returned path

#### Scenario: No images

- **WHEN** an entity has no images
- **THEN** `MediaError` is raised naming the entity

### Requirement: Preview audio download

`download_preview(entity, dest=".", *, filename=None, embed_cover=False)` SHALL download the preview MP3 of a `Track` or `Episode` and return the written `Path`. Entities whose `preview_url` is `None` SHALL raise `MediaError` explaining that no preview is available.

#### Scenario: Track preview

- **WHEN** a playable track's preview is downloaded
- **THEN** an MP3 file exists at the returned path and begins with an MP3 frame or ID3 header

### Requirement: Optional cover embedding

With `embed_cover=True`, the downloaded MP3 SHALL get the entity's cover art embedded as an ID3 APIC frame plus basic tags (title, artist where known) via mutagen. If the `media` extra is not installed, `MediaError` SHALL be raised with the install hint `pip install spotifyscraper[media]`.

#### Scenario: Embedded cover round-trip

- **WHEN** a preview is downloaded with `embed_cover=True` (mutagen installed)
- **THEN** reading the file back with mutagen shows an APIC frame whose data equals the downloaded cover bytes

#### Scenario: Missing extra

- **WHEN** `embed_cover=True` without mutagen installed
- **THEN** `MediaError` is raised mentioning `spotifyscraper[media]`

### Requirement: Safe filenames

Generated filenames SHALL strip path separators and control characters, collapse whitespace, preserve Unicode word characters, and be capped at 150 characters before the extension.

#### Scenario: Hostile entity name

- **WHEN** an entity is named `../../etc/passwd<>:"|?*`
- **THEN** the written file stays inside `dest` with a sanitized name

