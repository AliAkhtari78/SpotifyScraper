# MCP directory submissions

The #1 leverage move: a **no-API-key Spotify MCP** is near-unique (every other
Spotify MCP on PulseMCP wraps the official API and needs OAuth + a Developer
app). Lead every listing with that wedge.

**One-line description to reuse everywhere:**
> Extract public Spotify metadata, lyrics & podcasts for LLM agents — no API key,
> no OAuth, no Spotify Developer app. Sync+async, typed, read-only.

## 0. Official MCP Registry — automated ✅

Wired in v3.9.0 via `.github/workflows/publish-mcp.yml` (GitHub OIDC, no secret).
It publishes `server.json` on each release tag once the version is live on PyPI.
Downstream directories (Glama, mcp.so, PulseMCP) auto-crawl from here — do this
ONE thing and most of them populate for free. Verify after release:
`curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=spotifyscraper"`

## 1. punkpeye/awesome-mcp-servers (89k★) — highest-value PR

- Fork, add ONE line under the best-fit category (create a **Music/Media** bucket
  if none fits), alphabetical, format-exact.
- Entry:
  ```
  - [AliAkhtari78/SpotifyScraper](https://github.com/AliAkhtari78/SpotifyScraper) 🐍 🏠 - Public Spotify metadata, lyrics & podcasts with no API key or OAuth (sync+async, typed).
  ```
  (Use the repo's legend for the emoji: 🐍 = Python, 🏠 = local/stdio. Check
  CONTRIBUTING.md for the current legend before submitting.)
- The repo documents a `🤖🤖🤖` PR-title suffix to fast-track automated-agent PRs.

## 2. Glama (glama.ai/mcp) — claim + score

- Sign in with GitHub to **claim** the auto-crawled listing (moves it out of the
  anonymous pile, unlocks ranking). Optionally add a `glama.json`.
- Score = Tool Definition Quality (70%) + Server Coherence (30%); the server's
  per-tool docstrings already score well — aim for tier A.

## 3. mcp.so — submit

- "Submit" in the nav, or open a GitHub issue with name/description/repo.

## 4. PulseMCP — auto-crawls the registry within ~a week

- After step 0 propagates, claim/curate via their Discord; softly pitch the
  "Weekly Pulse" newsletter (editorial — no submit button, don't bank on it).

## 5. Smithery (smithery.ai) — score-driven ranking

- `smithery mcp publish` (or publish a `.mcpb`). Score rewards rich tool/server
  descriptions + complete metadata (homepage/repo/license) — all present.

## 6. Docker MCP Catalog (curated, high-trust) — uses the ghcr image you ship

- Fork `github.com/docker/mcp-registry`, add metadata per CONTRIBUTING, open a PR.
- Prefer the "Docker-built" tier (Docker signs/publishes the image). Live within
  ~24h of approval after an automated build/init/tool-list check.

## 7. Anthropic Connectors Directory — needs a REMOTE endpoint (do last)

- Requires a public **HTTPS** server (the code already supports streamable-HTTP).
  Deploy an **anonymous-only** instance (NEVER expose the `SPOTIFY_SP_DC` tools),
  add `readOnlyHint` annotations, write a privacy policy, submit at
  clau.de/mcp-directory-submission. Highest-intent placement, but real ongoing
  hosting/abuse cost — bank the free wins above first.

## Do NOT

- ❌ Spam 30 low-quality "MCP directory" clones — they auto-crawl the registry.
- ❌ List it as "just another Spotify MCP" — that buries it. Lead with no-API-key.
- ❌ Let listings go stale (the CI auto-publish keeps the version current).
