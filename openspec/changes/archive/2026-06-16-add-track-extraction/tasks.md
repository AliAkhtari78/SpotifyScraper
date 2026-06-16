# Tasks: add-track-extraction

## 1. Pathfinder layer

- [x] 1.1 Implement `api/pathfinder.py` (Operation table, build_url, classify_response, auth_headers)

## 2. Parsers

- [x] 2.1 Implement `api/parse_entities.py` (parse_track_gql, parse_track_embed, _merge_tracks)

## 3. Clients

- [x] 3.1 Implement `_sync/client.py` SpotifyClient with get_track (embed-first two-tier flow)
- [x] 3.2 Implement `_async/client.py` AsyncSpotifyClient mirror
- [x] 3.3 Export public API from `__init__.py`

## 4. Tests

- [x] 4.1 `tests/unit/api/test_pathfinder.py`
- [x] 4.2 `tests/unit/api/test_parse_track.py` (fixture-driven)
- [x] 4.3 `tests/unit/test_client.py` + `tests/unit/test_client_async.py` + parity test
- [x] 4.4 `tests/live/test_track.py` (marked live)

## 5. Verify

- [x] 5.1 `make lint`, `make type`, `make test` green; live smoke passes both tiers
