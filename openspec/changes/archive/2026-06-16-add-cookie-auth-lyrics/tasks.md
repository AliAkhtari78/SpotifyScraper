# Tasks: add-cookie-auth-lyrics

## 1. Cookie auth

- [x] 1.1 auth/cookies.py (load_sp_dc, CookieTokenProvider + async mirror)
- [x] 1.2 Validate the token-exchange endpoint live with a real sp_dc; update design notes with the confirmed shape

## 2. Lyrics

- [x] 2.1 parse_lyrics in api/parse_entities.py
- [x] 2.2 get_lyrics on both clients (lazy provider construction, 404/401 classification)

## 3. Tests

- [x] 3.1 Unit: cookie ingestion table, provider lifecycle, classification, hygiene
- [x] 3.2 Live: skipif-gated sp_dc exchange + lyrics fetch

## 4. Verify

- [x] 4.1 All gates green
