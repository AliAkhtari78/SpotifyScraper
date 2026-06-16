# Design: add-media-downloads

## media/images.py (pure helpers + transport-using download)

```python
def pick_image(images: Sequence[Image], size: Literal["largest", "smallest"]) -> Image   # MediaError if empty
def safe_filename(name: str, max_length: int = 150) -> str
def extension_from_content_type(content_type: str | None) -> str    # image/jpeg->jpg, image/png->png, default jpg
def download_cover_sync(transport: Transport, entity: HasImagesAndName, dest: Path, *, size, filename) -> Path
async def download_cover_async(...)
```

`HasImagesAndName` is a small Protocol (`name: str`, `images: tuple[Image, ...]`) — every entity model satisfies it structurally; Track uses album images fallback when its own are empty.

## media/audio.py

```python
def download_preview_sync(transport, entity, dest, *, filename, embed_cover) -> Path
async def download_preview_async(...)
def _embed_cover(mp3_path: Path, cover_bytes: bytes, *, title: str, artist: str | None) -> None
    # lazy 'import mutagen.id3' inside; ImportError -> MediaError("pip install spotifyscraper[media]")
    # ID3: TIT2 title, TPE1 artist, APIC image/jpeg cover
```

Accepts `Track | Episode`; artist for tags = first artist name (tracks) / show name (episodes). Binary writes go through `Path.write_bytes` after full download (previews are ~350KB; no streaming needed).

## Client surface

```python
def download_cover(self, entity, dest=".", *, size="largest", filename=None) -> Path
def download_preview(self, entity, dest=".", *, filename=None, embed_cover=False) -> Path
```

Both accept entity models (not URLs) — composing `get_track` + `download_preview` keeps one obvious way to do things. Async mirrors return the same `Path`.

## Testing

Unit: pick_image/safe_filename/extension tables; respx-fed fake bytes for downloads into tmp_path; embed_cover round-trip with mutagen (dev deps include mutagen for tests); MediaError cases (no images, no preview, missing-extra via monkeypatched import). Live: download real cover + preview for the canonical track into tmp_path, assert JPEG/MP3 magic bytes; embed_cover round-trip APIC == cover bytes.
