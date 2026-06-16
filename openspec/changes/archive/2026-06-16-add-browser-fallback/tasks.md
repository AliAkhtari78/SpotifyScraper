# Tasks: add-browser-fallback

## 1. Browser package

- [x] 1.1 browser/__init__.py import guard with install-hint ImportError
- [x] 1.2 browser/playwright.py (PlaywrightTransport + async mirror, lazy start, error mapping)

## 2. Test infrastructure

- [x] 2.1 Register `browser` pytest marker; exclude from default run
- [x] 2.2 tests/browser/test_playwright_transport.py (+ ImportError test in default suite)

## 3. CI

- [x] 3.1 Non-blocking `browser` job in ci.yml (chromium install + -m browser)

## 4. Verify

- [x] 4.1 Gates green; live browser fetch works locally
