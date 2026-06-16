# Proposal: add-media-downloads

## Why

Downloading cover art and 30-second preview clips is the feature SpotifyScraper is best known for. v3 rebuilds it on the typed models, with safe filenames, deterministic destinations, and optional embedded cover art via mutagen (replacing v2's abandoned eyeD3).

## What Changes

- New `media/images.py`: download cover art for any entity model, with size selection and filename sanitization.
- New `media/audio.py`: download track/episode preview MP3s; optionally embed the cover as ID3 APIC via mutagen (lazy import behind the `media` extra).
- Clients gain `download_cover()` and `download_preview()` (sync + async).
- Failures raise `MediaError`; entities without media raise `MediaError` with a precise reason.

## Capabilities

### New Capabilities

- `media-downloads`: cover art and preview audio downloads with optional cover embedding

### Modified Capabilities

(none)

## Impact

- New package `src/spotify_scraper/media/`; client methods; `media` extra (mutagen) activates embedding
