# SpotifyScraper growth plan

Evidence-based plan to grow audience/stars, tailored to this repo's actual
numbers. Researched + adversarially evaluated (Opus 4.8, max effort) on
2026-06-20. This folder ships nothing to PyPI (`/extras` is excluded from the
sdist) — it's the playbook + ready-to-post copy.

## The one fact that reorders everything

**~5,000 PyPI downloads/month but only 265 stars** — a ~19:1 users-to-stargazers
ratio. Google is already the #1 traffic referrer; Reddit is barely present. So
this is primarily a **star-conversion + MCP-discovery** play, *not* a "get more
traffic" play. Most growth guides optimize for a big launch; for this repo the
cheapest wins are converting the audience that already exists.

## Prioritized roadmap (impact × effort × fit)

| # | Move | Status | Where |
|---|------|--------|-------|
| 1 | **Star-conversion**: README + docs CTAs, "vs spotipy" table, star-history, downloads badge, one-time CLI hint, social-preview image | ✅ shipped in v3.9.0 (image = manual upload, see below) | repo |
| 2 | **MCP distribution blitz**: official MCP registry + Glama/mcp.so/PulseMCP/Smithery + punkpeye list + topics | ✅ registry auto-publish wired (v3.9.0); directory submissions = `mcp-directories.md` | repo + PRs |
| 3 | **README-as-landing-page**: hero GIF (record the live demo), comparison table | table ✅; GIF = `TODO` (record from aliakhtari.com/spotify) | repo |
| 4 | **Coordinated 48h launch**: Show HN + Reddit | drafts ready → `launch/` | you post |
| 5 | **Awesome-lists**: awesome-python (hidden-gem lane), awesome-web-scraping, awesome-mcp | entries ready → `mcp-directories.md` + `awesome-lists.md` | PRs |
| 6 | **SEO content moat**: the spotipy-deprecation + no-API-key articles | draft ready → `seo/` | you publish |
| 7 | **Contributor funnel**: good-first-issues, fast Discussions | issues opened on GitHub | repo |

## What I shipped autonomously (v3.9.0)

- README: monthly-downloads badge, GitHub-stars badge, **honest "vs spotipy"
  comparison table**, the spotipy-deprecation wedge callout, a **star-history
  chart**, a bottom star CTA, and the `mcp-name` registry marker.
- Docs landing page: a "⭐ Find this useful?" star call-to-action.
- CLI: a **one-time, opt-out, stderr-only** star hint (`SPOTIFYSCRAPER_NO_HINT=1`
  to silence) — never pollutes piped/JSON/`--output`.
- MCP registry: `server.json`, Dockerfile ownership label, and a
  failure-isolated `publish-mcp` workflow (GitHub OIDC, no secret) that
  registers the server on every release tag.
- GitHub Topics expanded (mcp, mcp-server, model-context-protocol, llm, …).
- A batch of real `good first issue`s to seed the contributor funnel.

## What needs YOU (can't be done under your accounts by an agent)

1. **Upload the social-preview image** (`assets/social-preview.svg` → export PNG
   1280×640) at GitHub → Settings → Social preview. Lifts click-through on every
   shared link. (See `social-preview/`.)
2. **Record the hero GIF** from aliakhtari.com/spotify and drop it under the
   README hero (≤10 MB). The single biggest README conversion add still open.
3. **Post the launch** — `launch/show-hn.md` + `launch/reddit.md`, following
   `launch/posting-checklist.md`. Do it AFTER the GIF + social image are live.
4. **Open the directory/awesome PRs** that need your judgment on copy
   (`mcp-directories.md`, `awesome-lists.md`). Some I open for you; the rest are
   one-command each.
5. **Publish the SEO articles** (`seo/`) on aliakhtari.com (your ranking domain).

## Metrics to track (and honest targets)

- **Stars** (total + weekly delta) and **stars-per-1k-downloads** (the truest
  measure of fixing the 19:1 gap). Annotate the timeline with each ship date.
- PyPI downloads/day & /month (split by the `[mcp]` extra if possible).
- GitHub traffic uniques + referrers (watch Reddit/HN/MCP-directories vs Google).
- MCP registry/directory rank for "Spotify".
- **Star-authenticity guard:** watch for anomalous spikes from empty accounts —
  never buy stars or join star-exchange rings (GitHub deletes ~90% of flagged
  repos; it's an existential risk to a real-name OSS brand).

**Honest 90-day outlook (executing 1–5):** ~**450–650 stars** (a one-time launch
bump of ~+120–200 plus compounding conversion/discovery). Upside tail if HN
front-pages or it Trends: 900–1,200+. Downside (flat launch): ~350–450 — still a
clear win from the cheap conversion work. **1 year:** ~900–1,600, with a path
past 2,000 if the SEO + MCP positioning compound. Catching spotipy (~5k) in a
year is **not** realistic and isn't the goal — owning the "no-API-key Spotify +
MCP" niche is.

## Hard "do NOT do" list

- ❌ Buy stars / join star4star rings — ToS violation, FTC exposure, brand-fatal.
- ❌ Ask for HN/Reddit upvotes or seed fake praise — flags the post, can
  shadow-penalize aliakhtari.com. Seed genuine *questions* only.
- ❌ Spray the same post across many subs / ignore weekly-showcase rules.
- ❌ Over-claim: don't say it "replaces the Spotify API" or restores
  `audio-features` (it can't — Spotify deleted that data). Honesty converts.
- ❌ Star-nag on every CLI run or inside JSON/MCP output. (Shipped form is
  one-time, stderr, TTY-only, suppressible.)
- ❌ Add audio download to chase SpotiFLAC-style hype — off-scope, legal risk.
