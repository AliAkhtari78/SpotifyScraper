# Tasks: add-media-downloads

## 1. Media package

- [ ] 1.1 media/images.py (pick_image, safe_filename, extension mapping, sync+async cover download)
- [ ] 1.2 media/audio.py (sync+async preview download, lazy mutagen cover embedding)

## 2. Clients

- [ ] 2.1 download_cover / download_preview on both clients

## 3. Tests

- [ ] 3.1 Unit: pure helper tables + respx downloads + mutagen round-trip + MediaError cases
- [ ] 3.2 Live: real cover + preview download with magic-byte and APIC asserts

## 4. Verify

- [ ] 4.1 All gates green; add mutagen to dev dependency group
