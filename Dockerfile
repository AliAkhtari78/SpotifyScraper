# syntax=docker/dockerfile:1
#
# SpotifyScraper container image.
#
# By default it serves the MCP server over streamable-HTTP on :8000, so
#   docker run -p 8000:8000 ghcr.io/aliakhtari78/spotifyscraper
# gives you a hosted Model Context Protocol endpoint. Set SPOTIFY_SP_DC to enable
# the authenticated tools. Override the command to use the CLI instead, e.g.
#   docker run --rm ghcr.io/aliakhtari78/spotifyscraper spotifyscraper track <id>
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/AliAkhtari78/SpotifyScraper"
LABEL org.opencontainers.image.description="Extract public Spotify data without the official API — CLI + MCP server."
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the package with the CLI and MCP extras from source (hatchling reads
# the version from src/spotify_scraper/__init__.py, so the source must be present).
COPY pyproject.toml README.md LICENSE CHANGELOG.md ./
COPY src ./src
RUN pip install ".[cli,mcp]"

# Drop privileges.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

CMD ["spotifyscraper-mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
