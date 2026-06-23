# Launch posting checklist

Sequence matters: convert-then-launch. Don't fire the launch until the README
GIF + social-preview image are live (they materially raise conversion on the
traffic the launch sends).

## Pre-launch (do first)

- [ ] Social-preview image uploaded (GitHub → Settings → Social preview, 1280×640).
- [ ] Hero GIF under the README one-liner (record aliakhtari.com/spotify, ≤10 MB).
- [ ] v3.9.0 released; MCP server live in the official registry (verify:
      `curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=spotifyscraper"`).
- [ ] punkpeye/awesome-mcp-servers PR merged (so "now with an MCP server" has a link).
- [ ] aliakhtari.com/spotify confirmed CDN-cached for a 5k–30k visitor surge.
- [ ] 3–5 people lined up to ask **genuine questions** early (NOT upvotes, NOT praise).

## Launch day (one 48h window, Tue–Thu)

- [ ] **12:00–17:00 UTC**: post Show HN (`show-hn.md`), repo URL, plain title.
- [ ] Post the maker comment within 60 seconds.
- [ ] Same window: r/Python (showcase thread), r/coolgithubprojects, r/opensource,
      r/SideProject (`reddit.md`).
- [ ] Reply to every comment for the full day. Lead with substance + the honest scope.

## Hard don'ts (these backfire)

- ❌ Asking for upvotes / seeding fake praise (flags the post; can shadow-penalize
  aliakhtari.com).
- ❌ Top-level self-promo where a weekly thread is required.
- ❌ Identical copy spammed across many subs.
- ❌ Over-claiming vs spotipy (concede it wins on writes/private/market data).

## After

- [ ] Annotate the star-history timeline with the launch date.
- [ ] Note which channel converted best (HN vs each sub) to repeat next time.
- [ ] Reply to new issues/Discussions within ~24h to protect conversion.
