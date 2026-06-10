# Tasks: add-models-errors-urls

## 1. Foundations

- [ ] 1.1 Implement `errors.py` exception hierarchy
- [ ] 1.2 Implement `urls.py` (parse, entity_url, embed_url, entity_uri)
- [ ] 1.3 Implement `models/base.py` (`ModelBase` with reflective to_dict/from_dict)

## 2. Models

- [ ] 2.1 Implement `models/common.py` (Image, ArtistRef, AlbumRef, ShowRef, UserRef)
- [ ] 2.2 Implement `models/track.py`
- [ ] 2.3 Implement `models/album.py` and `models/artist.py`
- [ ] 2.4 Implement `models/playlist.py`, `models/episode.py`, `models/show.py`, `models/lyrics.py`
- [ ] 2.5 Wire `models/__init__.py` exports

## 3. Tests

- [ ] 3.1 `tests/unit/test_errors.py`
- [ ] 3.2 `tests/unit/test_urls.py` (parametrized table incl. intl/embed/URI/bare-ID/garbage)
- [ ] 3.3 `tests/unit/models/test_serialization.py` (round-trip + json.dumps for every model)

## 4. Verify

- [ ] 4.1 `make lint`, `make type`, `make test` all green
