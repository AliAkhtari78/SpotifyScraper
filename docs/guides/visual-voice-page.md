# Tutorial: build a visual, voice-driven Spotify page

This tutorial chains SpotifyScraper into a small, **visually rich** and
**voice-driven** web page: artwork-matched colors, a looping Canvas video, and an
LLM/voice layer powered by the [MCP server](mcp.md). It's the recipe behind the
[live demo](https://aliakhtari.com/spotify/).

You'll wire three layers:

1. **Data** — the library fetches typed, JSON-safe models.
2. **Visuals** — colors theme the page; the Canvas MP4 plays as the hero.
3. **Voice** — an MCP client (Claude or any LLM host) answers spoken questions
   by calling the same library as tools.

## 1. Fetch a rich payload

Gather everything a track page needs in a few calls. Public data is anonymous;
Canvas and credits need an `sp_dc` cookie (see
[authenticated sessions](authentication.md)).

```python
from spotify_scraper import SpotifyClient

def track_page(track_id: str, sp_dc: str | None = None) -> dict:
    with SpotifyClient(cookies=sp_dc) as client:
        track = client.get_track(track_id)
        colors = client.get_colors(track)                 # anonymous
        related = client.get_related_artists(track.artists[0].id)
        page = {
            "track": track.to_dict(),
            "colors": colors.to_dict(),
            "related": [a.to_dict() for a in related[:8]],
        }
        if sp_dc:                                          # logged-in extras
            canvas = client.get_canvas(track_id)
            page["canvas"] = canvas.to_dict() if canvas else None
            page["credits"] = client.get_credits(track_id).to_dict()
        return page
```

Every value is JSON-safe (`to_dict()`), so this dict drops straight into a
template or a JSON API response.

## 2. Theme the page and play the Canvas

Use the extracted colors for a gradient and the Canvas MP4 as a silent, looping
hero. A minimal template:

```html
<!-- colors.raw / colors.dark drive the gradient; canvas.url is a plain MP4 -->
<section style="background: linear-gradient(160deg, {{ colors.dark }}, {{ colors.raw }});">
  {% if canvas %}
    <video src="{{ canvas.url }}" autoplay loop muted playsinline></video>
  {% else %}
    <img src="{{ track.images[0].url }}" alt="{{ track.name }} cover" />
  {% endif %}
  <h1>{{ track.name }}</h1>
  <p>{{ track.artists[0].name }}</p>
</section>
```

The Canvas URL is a non-DRM MP4 on `canvaz.scdn.co`, so it streams in a plain
`<video>` tag with no extra player. See the
[colors & Canvas guide](visual.md) for the full field reference.

## 3. Add the voice / AI layer

Run the [MCP server](mcp.md) so an LLM host (Claude Desktop, a voice assistant,
or your own client) can answer questions by calling the library as tools — *"what
colors suit this album?"*, *"who produced this track?"*, *"summarize this
episode."*

Serve it over HTTP (or use the container) so a web front-end can reach it:

```bash
docker run -p 8000:8000 -e SPOTIFY_SP_DC="<sp_dc>" \
  ghcr.io/aliakhtari78/spotifyscraper
```

A browser voice flow then looks like: **mic → speech-to-text → your LLM (with the
MCP tools attached) → spoken answer**. The LLM calls `get_track`, `get_colors`,
`get_canvas`, `get_credits`, … and even returns inline cover art via
`get_cover_image`. Because the tools return structured JSON, the same payload can
update the visual page in step 2 as the user talks.

## Where to go next

- [Cover colors & Canvas](visual.md) · [Discovery](discovery.md) ·
  [Credits & concerts](more.md) · [Charts](charts.md)
- [MCP server](mcp.md) for the full tool/resource/prompt list
- [Authenticated sessions](authentication.md) to obtain an `sp_dc` cookie
