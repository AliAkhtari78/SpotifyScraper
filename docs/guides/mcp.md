# MCP server

SpotifyScraper ships a [Model Context Protocol](https://modelcontextprotocol.io)
server, so Claude and other LLM hosts can call it as a tool — fetch tracks,
search, pull lyrics, colors, Canvas, credits, and more, with **no official API
key**.

## Install & run

```bash
pip install "spotifyscraper[mcp]"
spotifyscraper-mcp                       # stdio transport (for desktop hosts)
```

Set `SPOTIFY_SP_DC` to enable the authenticated tools (canvas, credits, user,
lyrics, transcript, account):

```bash
SPOTIFY_SP_DC="<your sp_dc cookie>" spotifyscraper-mcp
```

### Transports

| Transport | Command | Use |
|---|---|---|
| `stdio` (default) | `spotifyscraper-mcp` | Claude Desktop, IDE hosts |
| `streamable-http` | `spotifyscraper-mcp --transport streamable-http --host 0.0.0.0 --port 8000` | A hosted endpoint a web app can call |
| `sse` | `spotifyscraper-mcp --transport sse` | Legacy SSE hosts |

### Run it as a container

The published image serves the HTTP transport out of the box:

```bash
docker run -p 8000:8000 \
  -e SPOTIFY_SP_DC="<your sp_dc cookie>" \
  ghcr.io/aliakhtari78/spotifyscraper
```

## Use it from Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "spotifyscraper": {
      "command": "spotifyscraper-mcp",
      "env": { "SPOTIFY_SP_DC": "<your sp_dc cookie>" }
    }
  }
}
```

Then ask Claude things like *"summarize this Spotify episode from its
transcript"* or *"what colors should I theme this album page with?"*.

## What the server exposes

- **Tools** — every getter: `get_track` / `get_album` / `get_artist` /
  `get_playlist` / `get_episode` / `get_show`, `search`, `list_charts` /
  `get_chart`, `get_related_artists`, `get_discography`, `get_similar_albums`,
  `get_colors`, `get_canvas`, `get_user`, `get_credits`, `get_artist_events`,
  `get_lyrics`, `get_transcript`, `get_account`, and `get_cover_image` (returns
  inline image content). Each returns structured JSON; authenticated tools
  advertise the `SPOTIFY_SP_DC` requirement and return a clear error without it.
- **Resources** — the six entities are addressable: `spotify://track/{id}`,
  `spotify://album/{id}`, `spotify://artist/{id}`, `spotify://playlist/{id}`,
  `spotify://episode/{id}`, `spotify://show/{id}`.
- **Prompts** — `describe_album`, `playlist_blurb`, `summarize_episode`.

## Build a server in code

```python
from spotify_scraper.mcp import build_server

server = build_server(sp_dc="<your sp_dc cookie>")
server.run(transport="stdio")
```
