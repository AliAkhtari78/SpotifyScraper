# Design: add-album-artist-playlist

Payload ground truth: `tests/fixtures/pathfinder/{album,artist,playlist}.json` and `tests/fixtures/embed/{album,artist,playlist}.json`.

## Pathfinder operations (add to OPERATIONS)

```python
"album":    Operation("getAlbum", "b9bfabef66ed756e5e13f68a942deb60bd4125ec1f1be8cc42769dc0259b4b10",
                      lambda eid: {"uri": f"spotify:album:{eid}", "locale": "", "offset": 0, "limit": 50}),
"artist":   Operation("queryArtistOverview", "ae0e2958a4ab645b35ca19ac04d0495ae12d9c5d7b7286217674801a9aab281a",
                      lambda eid: {"uri": f"spotify:artist:{eid}", "locale": "", "includePrerelease": False}),
"playlist": Operation("fetchPlaylist", "a65e12194ed5fc443a1cdebed5fabe33ca5b07b987185d63c72483867ad13cb4",
                      lambda eid: {"uri": f"spotify:playlist:{eid}", "offset": 0, "limit": 100,
                                   "enableWatchFeedEntrypoint": False}),
```

Pagination needs offset overrides: extend `build_url(kind, entity_id, *, variable_overrides: Mapping[str, Any] | None = None)` — overrides merge into the built variables (used for `offset`/`limit` paging). This is an additive, backward-compatible signature change.

## GraphQL → model mappings

### Album (`data.albumUnion`)
name, uri; id from uri tail; album_type = `type` lowercased; images = `coverArt.sources` (url/width/height); release_date = `date.isoString`; artists = `artists.items[]` → (profile.name? no — `items[].profile.name` not present here; use `items[].profile.name` if present else `items[].name`... fixture shows `artists.items[].profile.name` + `id`+`uri`+`visuals`) → ArtistRef(name, uri, id); label; copyrights = `copyright.items[].text`; total_tracks = `tracksV2.totalCount`; share_url = `sharingInfo.shareUrl`; tracks: each `tracksV2.items[].track` → Track(id from uri, uri, name, duration_ms=duration.totalMilliseconds, explicit=contentRating.label=="EXPLICIT", playable=playability.playable, artists=artists.items[]→profile.name+uri, play_count=playcount str→int, track_number=trackNumber, images=() — album art lives on the Album, preview_url=None, release_date=None).

### Artist (`data.artistUnion`)
name = `profile.name`; images = `visuals.avatarImage.sources`; biography = `profile.biography.text` (may be None); followers/monthly_listeners/world_rank from `stats` (worldRank 0 → None); external_links = `profile.externalLinks.items[].url`; share_url = `sharingInfo.shareUrl`; top_tracks = `discography.topTracks.items[].track` → sparse Track (id, uri, name, duration_ms=duration.totalMilliseconds, playcount str→int, artists→profile.name, images=albumOfTrack.coverArt.sources, playable=playability.playable); albums = `discography.albums.items[].releases.items[0]` → AlbumRef(id, uri, name, images=coverArt.sources); singles likewise from `discography.singles`.

### Playlist (`data.playlistV2`)
name, description, uri; id from uri; owner = `ownerV2.data` → UserRef(name, uri); followers; images = `images.items[0].sources`; total_tracks = `content.totalCount`; share_url = `sharingInfo.shareUrl`; tracks = `content.items[]` → PlaylistTrack(added_at=addedAt.isoString, added_by=addedBy?.data→UserRef|None, track=itemV2.data → Track) — skip items whose `itemV2.data.__typename` != "Track" (local files/episodes); track mapping: name, uri (id from uri), duration_ms=trackDuration.totalMilliseconds, playcount str→int, artists=artists.items[]→profile.name+uri, images=albumOfTrack.coverArt.sources, explicit=contentRating.label, playable=playability.playable, album=albumOfTrack→AlbumRef.

## Embed (tier 2) mappings

Common envelope: name/title, uri, id, `visualIdentity.image[]` (url/maxWidth/maxHeight), subtitle.
- Album: subtitle is the artist display name → artists=(ArtistRef(name=subtitle),); trackList[] → sparse Tracks (title→name, uri, duration int, isExplicit, subtitle→artist name).
- Artist: trackList[] → top_tracks sparse Tracks.
- Playlist: trackList[] (~50) → PlaylistTrack(track=sparse Track, added_at=None); subtitle is owner display name → owner=UserRef(name=subtitle).

## Client methods (sync + async mirrors)

```python
def get_album(self, value: str) -> Album                                  # paginates all tracks
def get_artist(self, value: str) -> Artist
def get_playlist(self, value: str, *, max_tracks: int | None = 100) -> Playlist
```

Flow identical to get_track (embed-first: embed fetch primes token + provides fallback data; tier-1 attempt; degrade on ParsingError with warning). Pagination loop (pure helper in parse_entities: merge content pages) issues additional pathfinder requests with offset overrides; pagination failures mid-loop degrade to returning what was collected plus a warning (never lose the whole result to a tail-page failure).

## Testing

- Unit: parse functions against all six fixtures (exact value asserts: album name "Whenever You Need Somebody", 10 tracks; artist "Rick Astley", monthly_listeners > 0; playlist "Today's Top Hits", owner "Spotify"); pagination loop with respx multi-page sequence; local-file skip with synthesized item; embed fallbacks per entity.
- Live (`-m live`): one smoke per entity asserting the issue #93/#94 scenarios.
