# Tasks: add-browser-fallback

## 1. Browser package

- [ ] 1.1 browser/__init__.py import guard with install-hint ImportError
- [ ] 1.2 browser/playwright.py (PlaywrightTransport + async mirror, lazy start, error mapping)

## 2. Test infrastructure

- [ ] 2.1 Register `browser` pytest marker; exclude from default run
- [ ] 2.2 tests/browser/test_playwright_transport.py (+ ImportError test in default suite)

## 3. CI

- [ ] 3.1 Non-blocking `browser` job in ci.yml (chromium install + -m browser)

## 4. Verify

- [ ] 4.1 Gates green; live browser fetch works locally
