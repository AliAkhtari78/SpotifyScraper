# FAQ

### Is this legal? Does it violate Spotify's Terms of Service?

SpotifyScraper only reads pages and JSON that Spotify serves to anonymous web
visitors, and it never handles your password. That said, scraping may conflict
with Spotify's Terms of Service, so it is your responsibility to use the library
lawfully and politely. See [Legal & ToS](legal.md) for the full picture.

### Why doesn't it need an API key?

The library bootstraps an **anonymous access token** that Spotify embeds in its
own public embed pages, then uses Spotify's internal JSON endpoints — the same
ones the web player uses. No registration, client ID, or secret is required.

### Why are some fields `None`?

Extraction uses a two-tier ladder. **Tier 1** (Spotify's GraphQL API) returns
rich data like play counts and track numbers; **tier 2** (the embed page) is a
fallback with core fields only. When tier 1 is unavailable, tier-1-only fields
come back as `None`. This is by design, so a Spotify-side change degrades
gracefully instead of crashing.

### Can it download full songs?

**No.** It can download the **~30-second preview clips that Spotify publishes
publicly**, and cover art. It does not download, decrypt, or circumvent DRM on
full tracks. See [Media downloads](guides/media-downloads.md).

### How do I avoid getting rate-limited or blocked?

Keep the built-in rate limiting and retries enabled, and consider lowering the
rate or adding a proxy for heavy workloads. See
[Anti-ban & resilience](guides/anti-ban.md).

### Where are lyrics and the command-line interface?

Both are planned for **v3.1**. Lyrics require an authenticated cookie plus a
rotating token handshake and are being built carefully so they don't destabilize
the core library; the CLI follows right after.

### Something stopped working — Spotify probably changed their site. What do I do?

Because the library rides on Spotify's undocumented endpoints, occasional
breakage is expected. Update to the latest release first. If it still fails,
check the pinned `spotify-breakage` issue, and open a bug report with your
`spotifyscraper` version, the URL, and the full traceback.

### Sync or async?

Use `SpotifyClient` for simple scripts and `AsyncSpotifyClient` for concurrent
bulk work. They expose the same methods and return the same models — see the
[Async guide](guides/async.md).
