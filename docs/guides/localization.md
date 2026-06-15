# Localization

Pass `locale` to control the **language** that Spotify uses for localized display
names (artist names, titles transliterated into another script, and so on). It is
a display-language preference and nothing more.

```python
from spotify_scraper import SpotifyClient

# Per-client default — applies to every call:
with SpotifyClient(locale="ja-JP") as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    print(track.artists[0].name)            # e.g. リック・アストリー

    # Per-call override wins over the client default:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC", locale="de")
```

`locale` is accepted on the constructor and as a keyword on every entity getter
and on `search()`. It is sent as the HTTP `Accept-Language` header on both the
pathfinder and embed requests (including pagination). When omitted, behavior is
byte-identical to before (the transport's default `Accept-Language: en`).

## What `locale` accepts

A **BCP-47 language tag**:

- a bare primary language subtag (2–3 letters), normalized to lower-case —
  `"de"`, `"ja"`, `"en"`, `"por"`;
- or a language-region tag, returned unchanged — `"ja-JP"`, `"en-US"`, `"pt-BR"`,
  `"zh-Hant-TW"`.

Anything else raises `URLError` **before any network request**, at both
construction and per call:

```python
SpotifyClient(locale="deutsch")    # URLError: not a valid language tag
client.get_track(id, locale="x_y") # URLError
```

## What `locale` is *not*

!!! warning "`locale` is a language, not a country/market"
    `locale` is **not** an ISO-3166 country code. A bare country code like `"US"`
    or `"GB"` is meaningless as an `Accept-Language` value and is silently ignored
    by Spotify — it does **not** select a market.

`locale` changes only how names are *spelled*; it does **not**:

- filter regional **availability**, or
- vary **preview URLs** or playability.

On the anonymous extraction ladder this library uses, Spotify resolves the
country from the request **IP**, and its pathfinder GraphQL silently discards a
`market` variable — so there is deliberately **no** anonymous `market=` toggle
that would appear to work while changing nothing. True market/availability
filtering requires the authenticated Web API, which this library does not
implement anonymously. For region-specific results, point the client's `proxy`
at the target region instead.
