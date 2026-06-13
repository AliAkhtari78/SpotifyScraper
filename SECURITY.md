# Security Policy

## Supported versions

Security fixes are provided for the current **3.x** release line only.

| Version | Supported |
|---------|-----------|
| 3.x     | ✅        |
| 2.x     | ❌ (legacy; see the migration guide) |
| < 2.0   | ❌        |

## Reporting a vulnerability

Please report security issues **privately** using GitHub's
[private vulnerability reporting](https://github.com/AliAkhtari78/SpotifyScraper/security/advisories/new)
(the **Security** tab → *Report a vulnerability*). Do not open a public issue
for a security problem.

You can expect an initial response within a few days. Coordinated disclosure is
appreciated; please allow up to 90 days for a fix before public disclosure.

## Scope

In scope: the `spotifyscraper` package and its handling of user-supplied input,
files, and credentials (e.g. cookies). Out of scope: Spotify's own services and
endpoints, which are not operated by this project.

## Credential handling

SpotifyScraper never transmits user credentials anywhere except to Spotify
itself. If you find a case where a token, cookie, or other secret could leak
(into logs, exceptions, or saved fixtures), please report it as a vulnerability.
