# Show HN draft

Post the **GitHub repo URL** (not a branded link). Tue–Thu, **12:00–17:00 UTC**.
Be present to reply for the full first hour (front page needs ~30–50 upvotes in
hour 1; reply within 60 min). Never ask for upvotes.

## Title (pick one — factual, not salesy)

- `Show HN: SpotifyScraper – public Spotify data in Python, no API key (now with an MCP server)`
- `Show HN: Pull Spotify metadata, lyrics and podcasts in Python without the API`

(The arXiv launch study found the "Show HN" tag confers no edge after controls —
so a plain factual title is fine; execution + timing + discussion are what matter.)

## First comment (post within 60 seconds, from your account)

> Author here. I built this because the official Spotify Web API makes you
> register an app, manage a client secret, and do an OAuth dance just to read
> public catalog data — and in Nov 2024 it deprecated `audio-features`,
> `recommendations` and `related-artists` for new apps with no replacement.
>
> SpotifyScraper bootstraps an anonymous token from Spotify's own public *embed*
> pages and reads the same JSON the web player uses, returning typed, immutable
> Python models. Sync + async, one runtime dependency (httpx), `mypy --strict`.
>
> v3 is a clean-room rewrite. New in this release: it ships an **MCP server**
> (+ a container) so you can give Claude/any LLM live Spotify data with no key,
> and it's now in the official MCP registry.
>
> Honest scope, up front to pre-empt the obvious questions:
> - It reads only **public** data + the ~30-second previews Spotify itself
>   serves. It does **not** download full tracks or touch DRM.
> - It can't bring back `audio-features` (danceability/energy/tempo) — Spotify
>   removed that data entirely; no tool has it. It *does* still return related
>   artists + recommendations with no key.
> - Like any scraper it can break when Spotify changes its web payloads; there's
>   a daily canary + a two-tier fallback (pathfinder GraphQL → embed parse) to
>   absorb that.
>
> Try it without installing anything: https://aliakhtari.com/spotify/ — paste a
> Spotify link and it shows the typed data + the exact Python that produced it.
> Repo: https://github.com/AliAkhtari78/SpotifyScraper — happy to answer anything.

## If it stalls (<30 upvotes in the first hour)

Don't repost immediately. HN has a "second-chance" pool that re-surfaces good
submissions — a flat first attempt often gets a second shot a day or two later.
Do NOT delete-and-repost more than once.

## Expected outcome (from arXiv n=138 launch data)

Base case ≈ **+120–200 stars over 48h** for a repo this solid with a working
demo; median is moderate, front-page/Trending is the upside tail, not the plan.
