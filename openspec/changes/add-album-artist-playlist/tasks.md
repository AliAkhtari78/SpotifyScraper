# Tasks: add-album-artist-playlist

## 1. Pathfinder

- [x] 1.1 Add album/artist/playlist operations; extend build_url with variable_overrides

## 2. Parsers

- [x] 2.1 parse_album_gql + parse_album_embed
- [x] 2.2 parse_artist_gql + parse_artist_embed
- [x] 2.3 parse_playlist_gql + parse_playlist_embed (+ page-merge helper, local-file skip)

## 3. Clients

- [x] 3.1 get_album / get_artist / get_playlist on SpotifyClient (with pagination)
- [x] 3.2 Async mirrors

## 4. Tests

- [x] 4.1 Unit parser tests against fixtures (exact-value asserts)
- [x] 4.2 Client tests incl. pagination and degradation (respx)
- [x] 4.3 Live smokes for #93/#94 scenarios

## 5. Verify

- [x] 5.1 All gates green
