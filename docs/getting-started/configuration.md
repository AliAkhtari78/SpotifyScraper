# Configuration Guide

This guide covers how to configure SpotifyScraper for optimal performance and your specific use case.

## Table of Contents
- [Basic Configuration](#basic-configuration)
- [Environment Variables](#environment-variables)
- [Client Settings](#client-settings)
- [Authentication Setup](#authentication-setup)
- [Performance Tuning](#performance-tuning)
- [Advanced Options](#advanced-options)
- [Configuration Files](#configuration-files)
- [Best Practices](#best-practices)

---

## Basic Configuration

### Default Configuration

SpotifyScraper works out of the box with sensible defaults:

```python
from spotify_scraper import SpotifyClient

# Basic client with defaults
client = SpotifyClient()
```

### Quick Configuration

```python
# Configure the most common settings
client = SpotifyClient(
    browser_type="requests",      # Use requests for speed
    log_level="INFO",            # Set logging level
    download_path="./downloads", # Default download location
    timeout=30                   # Request timeout in seconds
)
```

---

## Environment Variables

Set environment variables to configure SpotifyScraper without changing code:

### Basic Environment Variables

```bash
# Set in your shell or .env file
export SPOTIFY_SCRAPER_LOG_LEVEL=DEBUG
export SPOTIFY_SCRAPER_TIMEOUT=60
export SPOTIFY_SCRAPER_DOWNLOAD_PATH=/path/to/downloads
export SPOTIFY_SCRAPER_BROWSER_TYPE=selenium
export SPOTIFY_SCRAPER_COOKIE_FILE=/path/to/cookies.txt
```

### Loading from .env File

```python
import os
from dotenv import load_dotenv
from spotify_scraper import SpotifyClient

# Load environment variables from .env file
load_dotenv()

# Client will automatically use environment variables
client = SpotifyClient()
```

### Example .env File

```bash
# .env file
SPOTIFY_SCRAPER_LOG_LEVEL=INFO
SPOTIFY_SCRAPER_TIMEOUT=45
SPOTIFY_SCRAPER_DOWNLOAD_PATH=./music_downloads
SPOTIFY_SCRAPER_BROWSER_TYPE=requests
SPOTIFY_SCRAPER_USER_AGENT=SpotifyScraper/2.0.0
```

---

## Client Settings

### Browser Configuration

```python
# Use requests for speed (default)
client = SpotifyClient(browser_type="requests")

# Use Selenium for JavaScript-heavy content
client = SpotifyClient(browser_type="selenium")

# Use Selenium with specific browser
client = SpotifyClient(
    browser_type="selenium",
    selenium_browser="chrome",  # or "firefox", "edge"
    headless=True              # Run without GUI
)
```

### Timeout Settings

```python
client = SpotifyClient(
    timeout=30,           # General request timeout
    download_timeout=300, # Download timeout (5 minutes)
    retry_timeout=5       # Retry delay in seconds
)
```

### Logging Configuration

```python
import logging

client = SpotifyClient(
    log_level="DEBUG",           # DEBUG, INFO, WARNING, ERROR
    log_file="spotify.log",      # Log to file
    log_format="%(asctime)s - %(levelname)s - %(message)s"
)

# Or configure logging manually
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spotify_scraper.log'),
        logging.StreamHandler()
    ]
)
```

---

## Authentication Setup

### Cookie-Based Authentication

For premium features and higher rate limits:

```python
# Using cookie file
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Using cookie string
client = SpotifyClient(cookies="sp_dc=your_cookie_value; sp_key=your_key")

# Using cookie dictionary
cookies = {
    'sp_dc': 'your_sp_dc_value',
    'sp_key': 'your_sp_key_value'
}
client = SpotifyClient(cookies=cookies)
```

### Extracting Cookies from Browser

#### Method 1: Browser Export

1. Install a browser extension like "cookies.txt"
2. Navigate to open.spotify.com
3. Export cookies to a file
4. Use the file with SpotifyScraper

#### Method 2: Manual Extraction

1. Open Developer Tools (F12)
2. Go to Application/Storage tab
3. Find Cookies for open.spotify.com
4. Copy `sp_dc` and `sp_key` values

```python
# Use the extracted values
client = SpotifyClient(cookies={
    'sp_dc': 'AQBYourSpDcValueHere...',
    'sp_key': 'AQAYourSpKeyValueHere...'
})
```

---

## Performance Tuning

### Request Optimization

```python
client = SpotifyClient(
    max_retries=3,              # Retry failed requests
    retry_delay=1,              # Delay between retries
    concurrent_requests=5,       # Parallel requests limit
    request_delay=0.1,          # Delay between requests
    use_cache=True,             # Enable response caching
    cache_size=1000             # Cache size (number of responses)
)
```

### Caching Configuration

```python
# Enable disk-based caching
client = SpotifyClient(
    cache_type="disk",          # "memory", "disk", or "redis"
    cache_dir="./cache",        # Cache directory
    cache_expiry=3600          # Cache expiry in seconds
)

# Redis caching (requires redis-py)
client = SpotifyClient(
    cache_type="redis",
    redis_host="localhost",
    redis_port=6379,
    redis_db=0
)
```

### Batch Processing

```python
# Optimize for batch operations
client = SpotifyClient(
    batch_size=50,              # Process items in batches
    batch_delay=2,              # Delay between batches
    parallel_downloads=10       # Parallel downloads
)
```

---

## Advanced Options

### Proxy Configuration

```python
# HTTP proxy
client = SpotifyClient(
    proxy="http://proxy.example.com:8080"
)

# SOCKS proxy
client = SpotifyClient(
    proxy="socks5://proxy.example.com:1080"
)

# Proxy with authentication
client = SpotifyClient(
    proxy="http://user:pass@proxy.example.com:8080"
)

# Rotating proxies
proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080"
]
client = SpotifyClient(proxy_rotation=proxies)
```

### User Agent Customization

```python
# Custom user agent
client = SpotifyClient(
    user_agent="Mozilla/5.0 (Custom Browser) SpotifyScraper/2.0.0"
)

# Random user agents
client = SpotifyClient(
    user_agent_rotation=True,   # Use random user agents
    user_agent_list=[          # Custom user agent list
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
)
```

### Rate Limiting

```python
# Configure rate limiting
client = SpotifyClient(
    rate_limit=True,            # Enable rate limiting
    requests_per_minute=60,     # Max requests per minute
    burst_limit=10,             # Allow burst requests
    rate_limit_strategy="token_bucket"  # "fixed_window" or "token_bucket"
)
```

---

## Configuration Files

### JSON Configuration

Create a `spotify_config.json` file:

```json
{
    "browser_type": "requests",
    "timeout": 30,
    "log_level": "INFO",
    "download_path": "./downloads",
    "max_retries": 3,
    "use_cache": true,
    "cache_size": 1000,
    "proxy": null,
    "user_agent": "SpotifyScraper/2.0.0"
}
```

Load configuration:

```python
import json
from spotify_scraper import SpotifyClient

# Load configuration from file
with open('spotify_config.json', 'r') as f:
    config = json.load(f)

client = SpotifyClient(**config)
```

### YAML Configuration

Create a `spotify_config.yaml` file:

```yaml
browser_type: requests
timeout: 30
log_level: INFO
download_path: ./downloads
max_retries: 3
use_cache: true
cache_size: 1000
proxy: null
user_agent: SpotifyScraper/2.0.0

# Authentication
cookies:
  sp_dc: your_sp_dc_value
  sp_key: your_sp_key_value

# Performance
performance:
  concurrent_requests: 5
  request_delay: 0.1
  batch_size: 50
```

Load YAML configuration:

```python
import yaml
from spotify_scraper import SpotifyClient

# Load configuration from YAML
with open('spotify_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Extract main config and nested sections
main_config = {k: v for k, v in config.items() 
               if k not in ['cookies', 'performance']}
main_config.update(config.get('performance', {}))

client = SpotifyClient(
    cookies=config.get('cookies'),
    **main_config
)
```

---

## Best Practices

### Production Configuration

```python
# Recommended production settings
client = SpotifyClient(
    browser_type="requests",        # Faster for most use cases
    timeout=45,                     # Reasonable timeout
    max_retries=3,                  # Handle temporary failures
    log_level="WARNING",            # Reduce log noise
    use_cache=True,                 # Improve performance
    cache_size=5000,               # Large cache for production
    rate_limit=True,               # Respect rate limits
    requests_per_minute=30,         # Conservative rate limit
    user_agent_rotation=True        # Avoid detection
)
```

### Development Configuration

```python
# Recommended development settings
client = SpotifyClient(
    browser_type="selenium",        # Better for debugging
    timeout=60,                     # Longer timeout for debugging
    log_level="DEBUG",             # Detailed logging
    log_file="debug.log",          # Log to file
    max_retries=1,                 # Fail fast in development
    use_cache=False,               # Fresh data for testing
    headless=False                 # See browser for debugging
)
```

### Security Considerations

```python
# Secure configuration practices
import os

client = SpotifyClient(
    # Don't hardcode sensitive data
    cookies=os.getenv('SPOTIFY_COOKIES'),
    proxy=os.getenv('PROXY_URL'),
    
    # Use secure defaults
    verify_ssl=True,               # Verify SSL certificates
    timeout=30,                    # Prevent hanging requests
    max_retries=3,                 # Limit retry attempts
    
    # Log security events
    log_level="INFO",
    audit_log=True                 # Enable audit logging
)
```

### Resource Management

```python
# Always use context managers
with SpotifyClient() as client:
    track = client.get_track_info(url)
    # Client automatically closed

# Or manually manage resources
client = SpotifyClient()
try:
    track = client.get_track_info(url)
finally:
    client.close()  # Always close the client
```

---

## Configuration Validation

### Validate Settings

```python
def validate_config(config):
    """Validate configuration settings."""
    required_keys = ['browser_type', 'timeout']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")
    
    if config['timeout'] <= 0:
        raise ValueError("Timeout must be positive")
    
    if config['browser_type'] not in ['requests', 'selenium']:
        raise ValueError("Invalid browser_type")
    
    return True

# Use validation
config = {...}
validate_config(config)
client = SpotifyClient(**config)
```

### Environment-Specific Configs

```python
import os

# Load different configs based on environment
env = os.getenv('ENVIRONMENT', 'development')

config_files = {
    'development': 'config/dev.json',
    'staging': 'config/staging.json',
    'production': 'config/prod.json'
}

with open(config_files[env], 'r') as f:
    config = json.load(f)

client = SpotifyClient(**config)
```

---

## Troubleshooting Configuration

### Common Configuration Issues

1. **SSL Certificate Errors**:
   ```python
   client = SpotifyClient(verify_ssl=False)  # Not recommended for production
   ```

2. **Timeout Issues**:
   ```python
   client = SpotifyClient(timeout=120)  # Increase timeout
   ```

3. **Rate Limiting**:
   ```python
   client = SpotifyClient(
       requests_per_minute=10,  # Reduce rate
       request_delay=1          # Add delay
   )
   ```

4. **Memory Issues**:
   ```python
   client = SpotifyClient(
       cache_size=100,          # Reduce cache size
       concurrent_requests=2    # Reduce parallelism
   )
   ```

### Debug Configuration

```python
# Enable debug mode for troubleshooting
client = SpotifyClient(
    log_level="DEBUG",
    debug=True,                 # Enable debug mode
    debug_requests=True,        # Log all requests
    debug_responses=True,       # Log response details
    save_debug_files=True       # Save debug data to files
)
```

---

## Next Steps

Now that you have SpotifyScraper configured:

1. 🔐 Set up [authentication](../guide/authentication.md) for premium features
2. 📖 Learn [basic usage patterns](../guide/basic-usage.md)
3. 🚀 Explore [advanced examples](../examples/advanced.md)
4. 🛠️ Handle [errors gracefully](../guide/error-handling.md)

---

## Getting Help

If you need help with configuration:

1. Check the [FAQ](../faq.md) for common issues
2. Review [troubleshooting guide](../troubleshooting.md)
3. Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
4. Report bugs on [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)