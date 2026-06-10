# Tasks: add-anonymous-token

## 1. Embed parsing

- [ ] 1.1 Implement `api/parse_embed.py` (extract_next_data, get_entity, get_session, EmbedSession)

## 2. Token provider

- [ ] 2.1 Implement `auth/anonymous.py` (AnonymousTokenProvider + async mirror, shared staleness helper)

## 3. Tests

- [ ] 3.1 `tests/unit/api/test_parse_embed.py` against all six embed fixtures + error cases
- [ ] 3.2 `tests/unit/auth/test_anonymous.py` (cache, expiry skew, invalidate, TokenError hygiene)

## 4. Verify

- [ ] 4.1 `make lint`, `make type`, `make test` green
