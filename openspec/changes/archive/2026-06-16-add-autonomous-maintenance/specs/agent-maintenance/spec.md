# agent-maintenance

## ADDED Requirements

### Requirement: Observe-mode breakage diagnosis

The repository SHALL run an automated maintenance agent
(`.github/workflows/claude.yml`) that, when the daily canary files a
`spotify-breakage` issue (or a trusted maintainer mentions `@claude`), reproduces
the failure on the **anonymous** path and comments a root-cause diagnosis, governed
by `policy/agent.md`. At this rung the agent SHALL open no pull request, change no
files, and access no secret (it never needs `SPOTIFY_SP_DC`). It SHALL authenticate
with an API key, never a consumer-subscription OAuth token.

#### Scenario: Breakage diagnosed

- **WHEN** a `spotify-breakage` issue is open and the `AGENT_ENABLED` repo variable is `true`
- **THEN** the agent comments a root-cause diagnosis on the issue without opening a PR, changing files, or using a secret

#### Scenario: Kill switch

- **WHEN** the `AGENT_ENABLED` repo variable is absent or not `true`
- **THEN** the agent does not run

### Requirement: Least privilege and bounded autonomy

The maintenance agent SHALL run with least-privilege permissions (observe =
`contents: read` + `issues: write` only), an allowlisted tool set, and a bounded
turn budget. Any increase in autonomy (per `policy/promotion.md`) SHALL require an
explicit human edit to the workflow — it SHALL NOT escalate itself. Invocation via
`@claude` SHALL be restricted to trusted repository associations.

#### Scenario: Untrusted invocation rejected

- **WHEN** a user who is not an OWNER, MEMBER, or COLLABORATOR comments `@claude`
- **THEN** the agent does not run

#### Scenario: Promotion is human-gated

- **WHEN** the agent has produced correct diagnoses
- **THEN** it still cannot open a PR or merge until a human changes the workflow to grant that rung
