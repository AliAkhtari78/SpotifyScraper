# Design: add-podcast-entities

Ground truth: `tests/fixtures/pathfinder/{episode,show}.json`, `tests/fixtures/embed/{episode,show}.json`.

## Pathfinder operations (add to OPERATIONS)

```python
"episode": Operation("getEpisodeOrChapter", "3416929067571ac4b79db16716be3c6ea5f6265f7975a0ee94b1fc5ee1dc1e9d",
                     lambda eid: {"uri": f"spotify:episode:{eid}"}),
"show":    Operation("queryShowMetadataV2", "aaad798a17a43c0f443c45d630a83df39d2ca1062a090c2e4fb045d6b00ab360",
                     lambda eid: {"uri": f"spotify:show:{eid}"}),
```

## GraphQL → model mappings

### Episode (`data.episodeUnionV2`)
name, uri; id; description (plain `description`); duration_ms = `duration.totalMilliseconds`; explicit = `contentRating.label == "EXPLICIT"`; playable = `playability.playable`; release_date = `releaseDate.isoString`; images = `coverArt.sources`; preview_url = `previewPlayback.audioPreview.url` if present else None; show = `podcastV2.data` → ShowRef(uri→id, uri, name, publisher=publisher.name if present, images=coverArt.sources); share_url = `sharingInfo.shareUrl`.

### Show (`data.podcastUnionV2`)
name, uri, id; description; publisher = `publisher.name`; media_type = `mediaType`; images = `coverArt.sources`; total_episodes = `episodesV2.totalCount`; rating = `rating.averageRating` if present (float) else None; topics = `topics.items[].title`; share_url = `sharingInfo.shareUrl`; episodes = `episodesV2.items[].entity.data` → sparse Episode (name, uri, id, duration, releaseDate, coverArt, description if present, playable; show=None to avoid recursion).

## Embed (tier 2) mappings

- Episode entity: name/title, uri, id, duration int, `releaseDate.isoString`, `audioPreview.url`, explicit = `contentRatings.labels` contains "EXPLICIT" (case-insensitive) or isExplicit, images = `visualIdentity.image[]`, subtitle = show name → show=ShowRef(name=subtitle, id/uri from `relatedEntityUri`).
- Show entity: name/title, uri, id, subtitle = publisher → publisher, images = `visualIdentity.image[]`; episodes=() (embed page carries only the latest-episode envelope: do not fabricate a listing).

## Client methods

`get_episode(self, value: str) -> Episode`, `get_show(self, value: str) -> Show` — same embed-first two-tier flow; async mirrors.

## Testing

Unit: parse both fixtures with exact-value asserts (episode duration > 0, show name "The Joe Rogan Experience", publisher non-empty, total_episodes > 1000); degradation tests; embed parsers. Live: `get_episode` + `get_show` smokes asserting the issue #88 scenario.
