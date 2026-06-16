# Tasks: add-models-errors-urls

## 1. Foundations

- [x] 1.1 Implement `errors.py` exception hierarchy
- [x] 1.2 Implement `urls.py` (parse, entity_url, embed_url, entity_uri)
- [x] 1.3 Implement `models/base.py` (`ModelBase` with reflective to_dict/from_dict)

## 2. Models

- [x] 2.1 Implement `models/common.py` (Image, ArtistRef, AlbumRef, ShowRef, UserRef)
- [x] 2.2 Implement `models/track.py`
- [x] 2.3 Implement `models/album.py` and `models/artist.py`
- [x] 2.4 Implement `models/playlist.py`, `models/episode.py`, `models/show.py`, `models/lyrics.py`
- [x] 2.5 Wire `models/__init__.py` exports

## 3. Tests

- [x] 3.1 `tests/unit/test_errors.py`
- [x] 3.2 `tests/unit/test_urls.py` (parametrized table incl. intl/embed/URI/bare-ID/garbage)
- [x] 3.3 `tests/unit/models/test_serialization.py` (round-trip + json.dumps for every model)

## 4. Verify

- [x] 4.1 `make lint`, `make type`, `make test` all green
