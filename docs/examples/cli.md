# CLI Documentation

SpotifyScraper provides a powerful command-line interface for quick operations without writing Python code.

## Installation

After installing SpotifyScraper, the CLI is available as `spotify-scraper` or `spotifyscraper`:

```bash
# Check installation
spotify-scraper --version

# Or use the alternative command
spotifyscraper --help
```

## Basic Usage

### Getting Help

```bash
# General help
spotify-scraper --help

# Command-specific help
spotify-scraper track --help
spotify-scraper album --help
spotify-scraper playlist --help
spotify-scraper artist --help
```

## Track Commands

### Extract Track Information

```bash
# Basic track extraction
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6

# Save to JSON file
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --output track.json

# Pretty print with colors
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --pretty
```

### Download Track Preview

```bash
# Download preview MP3
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --download-preview

# Specify output directory
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --download-preview --output-dir ./music

# Download without cover art
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --download-preview --no-cover
```

### Download Track Cover

```bash
# Download cover image
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --download-cover

# Specify image size
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --download-cover --size large

# Available sizes: small, medium, large
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --download-cover --size small
```

### Extract Lyrics

```bash
# Extract lyrics (requires authentication)
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --lyrics --cookie-file cookies.txt

# Save lyrics to file
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --lyrics --cookie-file cookies.txt --output lyrics.txt

# Export as LRC format
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6 --lyrics --cookie-file cookies.txt --lrc
```

## Album Commands

### Extract Album Information

```bash
# Basic album extraction
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv

# Include full track list
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv --full-tracks

# Export to CSV
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv --format csv --output album.csv
```

### Download Album Cover

```bash
# Download album cover
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv --download-cover

# Download all available sizes
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv --download-cover --all-sizes
```

### Download All Album Previews

```bash
# Download all track previews from an album
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv --download-all-previews

# Specify output directory
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv --download-all-previews --output-dir ./album-previews
```

## Playlist Commands

### Extract Playlist Information

```bash
# Basic playlist extraction
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M

# Show only first N tracks
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --limit 10

# Export to different formats
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --format json
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --format csv --output playlist.csv
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --format markdown --output playlist.md
```

### Download Playlist Media

```bash
# Download playlist cover
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --download-cover

# Download all track previews
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --download-all-previews

# Download everything (covers + previews)
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --download-all --output-dir ./playlist-media
```

## Artist Commands

### Extract Artist Information

```bash
# Basic artist extraction
spotify-scraper artist https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb

# Include top tracks
spotify-scraper artist https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb --top-tracks

# Include discography statistics
spotify-scraper artist https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb --stats
```

### Download Artist Images

```bash
# Download artist image
spotify-scraper artist https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb --download-image

# Download all available images
spotify-scraper artist https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb --download-all-images
```

## Download Command

The unified download command for bulk operations:

```bash
# Download from multiple URLs
spotify-scraper download track1.txt track2.txt track3.txt

# Download from a file containing URLs
spotify-scraper download --from-file urls.txt

# Download with specific options
spotify-scraper download --from-file urls.txt --media all --output-dir ./downloads

# Download only previews
spotify-scraper download --from-file urls.txt --media audio

# Download only covers
spotify-scraper download --from-file urls.txt --media images
```

## Global Options

### Authentication

```bash
# Use cookie file for authenticated requests
spotify-scraper track URL --cookie-file cookies.txt

# Use specific headers
spotify-scraper track URL --header "User-Agent: CustomAgent" --header "Accept-Language: en"
```

### Proxy Configuration

```bash
# Use HTTP proxy
spotify-scraper track URL --proxy http://proxy.example.com:8080

# Use SOCKS proxy
spotify-scraper track URL --proxy socks5://proxy.example.com:1080
```

### Output Options

```bash
# Specify output format
spotify-scraper track URL --format json
spotify-scraper track URL --format csv
spotify-scraper track URL --format yaml

# Pretty print with colors
spotify-scraper track URL --pretty

# Quiet mode (no progress messages)
spotify-scraper track URL --quiet

# Verbose mode (debug output)
spotify-scraper track URL --verbose
```

### Browser Selection

```bash
# Use Selenium browser (for complex scenarios)
spotify-scraper track URL --browser selenium

# Use Selenium with specific driver
spotify-scraper track URL --browser selenium --driver chrome

# Run Selenium in headless mode
spotify-scraper track URL --browser selenium --headless
```

## Configuration File

Create a configuration file at `~/.spotify-scraper/config.json`:

```json
{
  "default_output_dir": "~/Music/SpotifyScraper",
  "cookie_file": "~/.spotify-scraper/cookies.txt",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "proxy": null,
  "browser": "requests",
  "rate_limit": 0.5,
  "timeout": 30,
  "retry_count": 3,
  "default_image_size": "large",
  "embed_cover": true,
  "log_level": "INFO"
}
```

Use with CLI:

```bash
# Use default config
spotify-scraper track URL

# Use custom config file
spotify-scraper --config ./custom-config.json track URL

# Override config options
spotify-scraper --config ~/.spotify-scraper/config.json track URL --browser selenium
```

## Batch Processing

### Using URLs File

Create a file `urls.txt`:
```
https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6
https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv
https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv
https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

Process all URLs:
```bash
# Extract information for all URLs
spotify-scraper batch urls.txt --output results.json

# Download all media
spotify-scraper batch urls.txt --download-all --output-dir ./batch-downloads

# Process with specific options
spotify-scraper batch urls.txt --format csv --download-preview --rate-limit 1.0
```

### Shell Script Integration

```bash
#!/bin/bash
# download_spotify_playlist.sh

PLAYLIST_URL=$1
OUTPUT_DIR=${2:-./downloads}

echo "Extracting playlist information..."
spotify-scraper playlist "$PLAYLIST_URL" --format json --output playlist_info.json

echo "Creating directory structure..."
mkdir -p "$OUTPUT_DIR/audio" "$OUTPUT_DIR/covers"

echo "Downloading all previews..."
spotify-scraper playlist "$PLAYLIST_URL" --download-all-previews --output-dir "$OUTPUT_DIR/audio"

echo "Downloading all covers..."
spotify-scraper playlist "$PLAYLIST_URL" --download-all-covers --output-dir "$OUTPUT_DIR/covers"

echo "Done! Files saved to $OUTPUT_DIR"
```

### Python Script Integration

```python
import subprocess
import json

def run_spotify_scraper(url, format='json'):
    """Run spotify-scraper CLI and return parsed output."""
    cmd = ['spotify-scraper', 'track', url, '--format', format]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        if format == 'json':
            return json.loads(result.stdout)
        else:
            return result.stdout
    else:
        raise Exception(f"Command failed: {result.stderr}")

# Usage
track_data = run_spotify_scraper("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
print(f"Track: {track_data['name']}")
```

## Advanced Examples

### Download Playlist with Metadata

```bash
# Create a complete playlist backup
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M \
  --download-all \
  --format json \
  --output playlist_metadata.json \
  --output-dir ./playlist_backup \
  --organize-by-artist \
  --embed-metadata
```

### Monitor Playlist Changes

```bash
# Check playlist for changes
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M \
  --format json \
  --output playlist_current.json

# Compare with previous version
diff playlist_previous.json playlist_current.json
```

### Export for Other Applications

```bash
# Export for iTunes/Apple Music
spotify-scraper playlist URL --format csv --itunes-compatible --output playlist.csv

# Export for VLC
spotify-scraper playlist URL --format m3u --output playlist.m3u

# Export for Plex
spotify-scraper playlist URL --format xml --plex-compatible --output playlist.xml
```

## Troubleshooting

### Debug Mode

```bash
# Enable debug logging
spotify-scraper --debug track URL

# Save debug log
spotify-scraper --debug track URL 2> debug.log

# Extreme verbosity
spotify-scraper --debug --verbose track URL
```

### Common Issues

```bash
# SSL Certificate errors
spotify-scraper track URL --no-verify-ssl

# Timeout issues
spotify-scraper track URL --timeout 60

# Rate limiting
spotify-scraper track URL --rate-limit 2.0

# Retry failed requests
spotify-scraper track URL --retry 5 --retry-delay 2
```

## Environment Variables

```bash
# Set cookie file
export SPOTIFY_SCRAPER_COOKIE_FILE=~/.spotify-cookies.txt

# Set default output directory
export SPOTIFY_SCRAPER_OUTPUT_DIR=~/Music/Spotify

# Set proxy
export SPOTIFY_SCRAPER_PROXY=http://proxy:8080

# Set log level
export SPOTIFY_SCRAPER_LOG_LEVEL=DEBUG

# Use environment variables
spotify-scraper track URL
```

## Tips and Tricks

1. **Aliases**: Create shell aliases for common operations
   ```bash
   alias sps='spotify-scraper'
   alias sps-track='spotify-scraper track'
   alias sps-dl='spotify-scraper download'
   ```

2. **Completion**: Enable tab completion
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   eval "$(_SPOTIFY_SCRAPER_COMPLETE=source spotify-scraper)"
   ```

3. **Parallel Downloads**: Use GNU Parallel for faster batch processing
   ```bash
   cat urls.txt | parallel -j 4 spotify-scraper track {} --download-preview
   ```

4. **Scheduled Downloads**: Use cron for regular playlist backups
   ```bash
   # Add to crontab
   0 2 * * * spotify-scraper playlist URL --download-all --output-dir ~/playlist-backup-$(date +\%Y\%m\%d)
   ```

5. **Integration with other tools**:
   ```bash
   # Pipe to jq for JSON processing
   spotify-scraper track URL --format json | jq '.name'
   
   # Use with youtube-dl for full songs
   spotify-scraper track URL --format json | jq -r '.name + " " + .artists[0].name' | xargs youtube-dl "ytsearch:"
   ```