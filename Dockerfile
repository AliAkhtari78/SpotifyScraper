# Multi-stage Dockerfile for SpotifyScraper

# Stage 1: Build stage
FROM python:3.13-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .
COPY setup.py .
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt
RUN pip install --user --no-warn-script-location .

# Stage 2: Runtime stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy installed packages from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Create app directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Switch to non-root user
USER appuser

# Set Chrome options for Selenium
ENV CHROME_BIN=/usr/bin/chromium \
    CHROME_DRIVER=/usr/bin/chromedriver

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import spotify_scraper; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "spotify_scraper"]

# Labels
LABEL org.opencontainers.image.title="SpotifyScraper" \
      org.opencontainers.image.description="Python library for extracting data from Spotify" \
      org.opencontainers.image.authors="Ali Akhtari" \
      org.opencontainers.image.source="https://github.com/AliAkhtari78/SpotifyScraper" \
      org.opencontainers.image.licenses="MIT"