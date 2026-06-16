# visual Specification

## Purpose

Cover-art color extraction and Canvas looping cover videos.

## Requirements
### Requirement: Cover-art color extraction

`get_colors(source)` SHALL return a frozen `Colors` model (`raw` / `dark` /
`light` `#RRGGBB` hex plus `is_fallback`) extracted anonymously from a cover
image, accepting an image URL, a `spotify:image:` uri, or any entity that has
images.

#### Scenario: Colors from an entity

- **WHEN** `get_colors(track)` is called on a cookie-less client
- **THEN** a `Colors` with three `#RRGGBB` values is returned using the anonymous
  bearer token, with no cookie exchanged

### Requirement: Track Canvas video

`get_canvas(track)` SHALL return a `Canvas` carrying a non-DRM looping MP4 `url`,
or `None` when the track has no Canvas, and MUST require the cookie-derived user
token.

#### Scenario: No cookie configured

- **WHEN** `get_canvas(track)` is called on a client built without cookies
- **THEN** `AuthenticationError` is raised before any HTTP request

#### Scenario: Track without a Canvas

- **WHEN** the `canvas` op returns a null canvas for the track
- **THEN** `None` is returned rather than an error

