# Tasks: release-v3-0-0

## 1. Finalize

- [ ] 1.1 Pre-flight: lint/type/test/docs-strict + one full live pass green on v3
- [ ] 1.2 Bump __version__ to 3.0.0; finalize CHANGELOG [3.0.0] section
- [ ] 1.3 Final README pass (badges, example, extras, legal, migration link)

## 2. Ship

- [ ] 2.1 Open v3 -> master PR, CI green, merge
- [ ] 2.2 Confirm PyPI trusted publisher + pypi environment exist
- [ ] 2.3 Tag v3.0.0; verify release pipeline publishes to PyPI + GitHub release

## 3. Post-release surfaces

- [ ] 3.1 Close issues #86/#88/#93/#94 with migration links
- [ ] 3.2 Push wiki stub; publish gh-pages redirect; set repo website to RTD
- [ ] 3.3 Publish blog post to aliakhtari.com
- [ ] 3.4 Verify RTD stable = v3.0.0

## 4. Verify

- [ ] 4.1 Clean-venv `pip install spotifyscraper==3.0.0` quickstart on 3.10 and 3.13
