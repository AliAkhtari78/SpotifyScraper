# Tasks: add-media-downloads

## 1. Media package

- [x] 1.1 media/images.py (pick_image, safe_filename, extension mapping, sync+async cover download)
- [x] 1.2 media/audio.py (sync+async preview download, lazy mutagen cover embedding)

## 2. Clients

- [x] 2.1 download_cover / download_preview on both clients

## 3. Tests

- [x] 3.1 Unit: pure helper tables + respx downloads + mutagen round-trip + MediaError cases
- [x] 3.2 Live: real cover + preview download with magic-byte and APIC asserts

## 4. Verify

- [x] 4.1 All gates green; add mutagen to dev dependency group
