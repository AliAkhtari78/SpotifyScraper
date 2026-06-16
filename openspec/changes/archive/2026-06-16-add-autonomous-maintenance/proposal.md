# Proposal: add-autonomous-maintenance

> **Status: shipped (rung 0 — observe).** An additive CI/governance surface: an
> automated agent that diagnoses canary-reported breakages. No library code, model,
> or CLI changes.

## Why

The repo already has **Sense** (the `canary.yml` daily live tests that file a
`spotify-breakage` issue on failure) and **Verify** (CI gates + OpenSpec). The
missing link is an automatic **Act**: today a human opens Claude Code by hand to
diagnose and fix. This adds the first, safest slice of that — an agent that
*diagnoses* a breakage and comments its findings — behind a governance contract,
a kill switch, and least privilege, so autonomy can be dialled up later on evidence.

## What Changes

- New `policy/` directory — the **Agent Operating Contract** (`agent.md`), per-role
  capability scopes (`scopes.yml`), and the autonomy ladder + kill switch
  (`promotion.md`).
- New `.github/workflows/claude.yml` — runs the Claude Code GitHub Action at
  **rung 0 (observe)**: on a `spotify-breakage` issue (or an owner `@claude`
  mention), it reproduces the failure on the anonymous path and comments a
  root-cause diagnosis. It opens nothing, changes no files, and touches no secret.
- `CLAUDE.md` gains an "Autonomous maintenance" section pointing the agent at the
  binding contract.
- Auth is an **API key** (`secrets.ANTHROPIC_API_KEY`), not subscription OAuth
  (ToS + CI-reliability reasons); a repo variable **`AGENT_ENABLED`** is the kill
  switch; `--max-turns` bounds cost.

## Impact

Additive and reversible. The library, its public API, the CLI, and the MCP server
are untouched. Promotion to "propose" (open a PR) or "auto-merge" is a deliberate,
human-made edit to the workflow — never automatic. Flipping `AGENT_ENABLED` off
silences the whole thing in one click.
