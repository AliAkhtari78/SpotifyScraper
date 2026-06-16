# Autonomy ladder

The agent's autonomy is a **dial**, not a switch — moved up only on evidence, and
revertible in a single commit (or by flipping the `AGENT_ENABLED` repo variable
off). Each rung has an **entry gate**: the record that must exist to climb.

**Current rung: 0 — Observe.**

| Rung | The agent may… | Human role | Climb when… |
|---|---|---|---|
| **0 · Observe** *(now)* | read the breakage issue, reproduce on the anonymous path, comment a diagnosis | does the fix | diagnoses are correct ~5 real cycles running |
| **1 · Propose** | open a labelled PR with a **proven** fix (Definition of Done met) | reviews + merges every PR | ≥ 20 PRs merged, ≤ 1 needing real edits |
| **2 · Auto-merge (narrow)** | auto-merge **hash-only** PRs (diff confined to `api/pathfinder.py`) when canary + CI are green | reviews everything else | 0 bad auto-merges over a quarter |
| **3 · Autonomous (scoped)** | auto-merge + auto-release patch fixes; triage/label; respond to issues | sets policy, audits weekly | sustained low escalation + clean audit |
| **4 · Fleet** | multi-repo, role-aware orchestration | owns the contract + roster | you stop being in any single loop |

## How a rung is enforced

The dial is **branch-protection settings + a few `if:`/`permissions:` lines** keyed
on labels and diff scope — not new code:

- **Rung 0 → 1:** change the workflow prompt from "diagnose only" to "open a PR with
  a proven fix"; grant the job `contents: write` + `pull-requests: write`; keep a
  required human review on `master`.
- **Rung 1 → 2:** drop the required human review **only** for PRs labelled
  `agent-autofix` whose diff touches **only** `src/spotify_scraper/api/pathfinder.py`;
  everything else still waits for a human.

## Kill switch

Set the repo variable `AGENT_ENABLED` to anything other than `true` (or delete it)
and the entire agent goes quiet immediately — no code change, no deploy. Use it the
moment anything looks wrong.

## Promotion log

Record each promotion here with the date and the evidence that justified it.

- _2026-06-16 — installed at rung 0 (Observe). No promotions yet._
