# Reddit drafts

Reddit was the single most effective channel in the case studies — but ONLY when
the copy reads like a person explaining a tool to a colleague, not marketing.
Post in the **same 48h window** as Show HN. Read each sub's rules first; use the
weekly showcase thread where a top-level post would break the self-promo rule.
Have prior comment history in the sub; never drive-by link-drop.

---

## r/Python (1.2M) — use the weekly "Showcase"/"What are you working on" thread unless a top-level post is clearly allowed

**Title:** I rewrote my no-API-key Spotify library (v3) — typed, async, and it now has an MCP server

> I maintain SpotifyScraper, a library that reads **public** Spotify data
> (tracks/albums/artists/playlists/podcasts/lyrics) without the official API —
> no app registration, no client secret, no OAuth. Just `pip install
> spotifyscraper` and call a method.
>
> I just finished a ground-up v3 rewrite and wanted to share what changed:
> - **Sync *and* async** clients, fully typed immutable models, `mypy --strict`,
>   one runtime dependency (httpx).
> - A **CLI** and an **MCP server** (+ container) so you can wire live Spotify
>   data into Claude/LLMs with no key.
> - Honest scope: public metadata + the ~30s previews Spotify publishes. No
>   full-track download, no DRM. It can't restore the `audio-features` endpoint
>   Spotify deprecated in 2024 (that data is gone everywhere), but it still
>   returns related artists + recommendations without a key.
>
> Live demo (no install): https://aliakhtari.com/spotify/
> Repo: https://github.com/AliAkhtari78/SpotifyScraper
>
> Happy to take feedback on the API design or the async story.

---

## r/coolgithubprojects (purpose-built for this) — top-level OK

**Title:** SpotifyScraper — public Spotify data in Python with no API key (sync+async, typed, MCP server)

> Reads public Spotify metadata/lyrics/podcasts without the official API or a key.
> v3 is a clean rewrite: typed models, sync+async, a CLI, and an MCP server for
> LLMs. Live no-install demo: https://aliakhtari.com/spotify/ · Repo:
> https://github.com/AliAkhtari78/SpotifyScraper

---

## r/opensource (210K) — limited self-promo OK; lead with the "why"

**Title:** A no-API-key Spotify data library (MIT) — and what I learned keeping a scraper alive for 6 years

> Short, honest write-up framing: the maintenance reality of a scraper (daily
> canary, two-tier fallback), why I keep it public-metadata-only on purpose
> (no audio/DRM), and the v3 rewrite + MCP server. Link the repo + demo.

---

## Notes

- r/programming top-level: skip unless you have a real technical write-up (strict
  rules). r/SideProject (131K) is fine for the demo angle.
- Answer every comment for the first day. The demo link is your edge everywhere.
- Do NOT cross-post identical text to many subs in a row — tailor each.
