# Legal & Terms of Service

!!! warning "Read before you use SpotifyScraper"
    SpotifyScraper is an independent, unofficial project. It is **not affiliated
    with, authorized, maintained, sponsored, or endorsed by Spotify** or any of
    its affiliates.

## Intended use

SpotifyScraper is provided for **educational purposes and personal use** —
learning about web data extraction, building hobby projects, and accessing
publicly available metadata. You are responsible for ensuring your use complies
with Spotify's [Terms of Service](https://www.spotify.com/legal/end-user-agreement/)
and any applicable laws in your jurisdiction.

## What the library does and does not do

- It reads **publicly accessible** pages and JSON endpoints that Spotify serves
  to anonymous web visitors. It does not require, request, or store your Spotify
  password.
- Audio previews are the **~30-second clips that Spotify itself publishes** for
  public playback. The library does **not** download, decrypt, or circumvent DRM
  on full tracks, and it will not help you do so.
- It does not bypass paywalls, rate limits put in place for abuse prevention, or
  any technical protection measure.

## Your responsibilities

- Respect rate limits and scrape politely. The library ships conservative
  defaults and retry/back-off behavior — please do not remove them to hammer
  Spotify's servers (see [Anti-ban & resilience](guides/anti-ban.md)).
- Do not redistribute Spotify's content in violation of their terms.
- Do not use the library to build a service that competes with or harms Spotify.

## No warranty

The software is provided "as is", without warranty of any kind, under the
[MIT License](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE).
Because it depends on Spotify's undocumented web endpoints, it may break at any
time when Spotify changes its site.

## Takedown / contact

If you are a rights holder or Spotify representative with a concern, please open
an issue or contact the maintainer at the address listed on
[the GitHub repository](https://github.com/AliAkhtari78/SpotifyScraper), and it
will be addressed promptly.
