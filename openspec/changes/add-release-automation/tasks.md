# Tasks: add-release-automation

## 1. Workflows

- [ ] 1.1 release.yml (version gate, trusted publishing, changelog-sectioned GitHub release)
- [ ] 1.2 canary.yml (daily live run, lyrics non-blocking job, issue open/update/close logic)

## 2. Repo configuration

- [ ] 2.1 dependabot.yml (weekly, grouped, conventional prefixes)
- [ ] 2.2 Issue forms (bug_report.yml, feature_request.yml, config.yml) + PR template
- [ ] 2.3 SECURITY.md

## 3. Manual steps (documented, done at release)

- [ ] 3.1 Configure PyPI trusted publisher + `pypi` GitHub environment
- [ ] 3.2 Add SPOTIFY_SP_DC secret (optional, enables lyrics canary)

## 4. Verify

- [ ] 4.1 workflow lint (actionlint or careful review); canary dry-run via workflow_dispatch on v3 branch
