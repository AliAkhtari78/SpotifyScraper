# show-episodes Specification

## Purpose
TBD - created by archiving change harden-reliability-and-completeness. Update Purpose after archive.
## Requirements
### Requirement: Complete show episode listing

`get_show(value, *, max_episodes=50)` SHALL populate `Show.total_episodes` and `Show.episodes` by paginating the `queryPodcastEpisodes` operation (page size 50) until `max_episodes` episodes are collected or the show is exhausted; `max_episodes=None` SHALL fetch every episode. `total_episodes` SHALL always report the show's full episode count.

#### Scenario: Default listing

- **WHEN** an active show with thousands of episodes is fetched with defaults
- **THEN** `show.total_episodes` is the full count and `show.episodes` holds the first 50 episodes, each with `name` and `duration_ms`

#### Scenario: Bounded listing

- **WHEN** `max_episodes=120` is requested
- **THEN** exactly 120 episodes are returned across multiple pages (for a show that large)

### Requirement: Graceful episode-listing failure

If the episode-listing operation fails after the show metadata is fetched, `get_show` SHALL return the show with whatever episodes were collected (possibly none) and a logged warning, rather than failing the whole fetch.

#### Scenario: Episode page error

- **WHEN** the metadata fetch succeeds but an episode page request fails
- **THEN** the returned `Show` has its metadata and a logged warning, and no exception propagates

