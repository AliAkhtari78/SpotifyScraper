# Tasks: add-autonomous-maintenance

- [x] `policy/agent.md` — Agent Operating Contract (Definition of Done, invariants,
      evidence standard, escalation, untrusted-input rule)
- [x] `policy/scopes.yml` — per-role tool/path allowlists + hard denylist
- [x] `policy/promotion.md` — autonomy ladder, current rung (0), `AGENT_ENABLED` kill switch
- [x] `.github/workflows/claude.yml` — observe-mode job: SHA-pinned action, API-key auth,
      least-privilege `permissions` (contents:read + issues:write), `--max-turns`,
      kill-switch + scope `if:`, `@claude` gated to OWNER/MEMBER/COLLABORATOR
- [x] `CLAUDE.md` — "Autonomous maintenance" section pointing at the contract
- [x] Set the `AGENT_ENABLED` repo variable; confirm `ANTHROPIC_API_KEY` secret exists
- [x] Live smoke test (owner-triggered `workflow_dispatch`, 2026-06-16): auth + the
      full action pipeline validated end-to-end; observe mode opened/posted/changed
      nothing; secrets stayed masked. First fix it surfaced: the action needs the
      job's `GITHUB_TOKEN` (commit `4974772`) to avoid the OIDC path. Diagnosis
      *quality* on a real breakage is ongoing operational validation; promotion to
      rung 1 is a separate, future change (see `policy/promotion.md`).
