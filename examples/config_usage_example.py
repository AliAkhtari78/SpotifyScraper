#!/usr/bin/env python3
"""
Example demonstrating configuration management with SpotifyScraper.

This example shows how to use the Config class to:
- Create and modify configuration
- Save and load configuration from files
- Use environment variables
"""

import json
from pathlib import Path

from spotify_scraper import Config, SpotifyClient


def main():
    """Demonstrate configuration features."""

    print("=== SpotifyScraper Configuration Example ===\n")

    # 1. Create default configuration
    print("1. Creating default configuration...")
    config = Config()
    print(f"   Browser type: {config.get('browser_type')}")
    print(f"   Log level: {config.get('log_level')}")
    print(f"   Cache enabled: {config.get('cache_enabled')}")
    print(f"   Auth token: {config.get('auth_token')}")

    # 2. Update configuration programmatically
    print("\n2. Updating configuration...")
    config.set("log_level", "DEBUG")
    config.set("cache_enabled", True)
    config.set("cache_ttl", 7200)  # 2 hours
    config.set("auth_token", "example_token_123")

    print(f"   Updated log level: {config.get('log_level')}")
    print(f"   Updated cache TTL: {config.get('cache_ttl')} seconds")
    print(f"   Updated auth token: {config.get('auth_token')}")

    # 3. Save configuration to file
    print("\n3. Saving configuration to file...")
    config_file = Path("spotify_config.json")
    try:
        config.save(config_file)
        print(f"   Configuration saved to {config_file}")
    except Exception as e:
        print(f"   Error saving config: {e}")

    # 4. Load configuration from file
    print("\n4. Loading configuration from file...")
    new_config = Config(config_file=config_file)
    print(f"   Loaded log level: {new_config.get('log_level')}")
    print(f"   Loaded auth token: {new_config.get('auth_token')}")

    # 5. Environment variable configuration
    print("\n5. Environment variable configuration...")
    print("   You can set environment variables like:")
    print("   export SPOTIFY_SCRAPER_LOG_LEVEL=DEBUG")
    print("   export SPOTIFY_SCRAPER_CACHE_ENABLED=true")
    print("   export SPOTIFY_SCRAPER_AUTH_TOKEN=your_token_here")

    # Demonstrate environment variable usage
    os.environ["SPOTIFY_SCRAPER_LOG_LEVEL"] = "WARNING"
    env_config = Config(use_env=True)
    print(f"\n   Config from env: log_level = {env_config.get('log_level')}")

    # 6. Create client with configuration
    print("\n6. Creating SpotifyClient...")
    try:
        # Note: SpotifyClient doesn't directly use Config object
        # You need to pass parameters individually
        client = SpotifyClient(
            log_level=config.get("log_level", "INFO"),
            cookie_file=config.get("cookie_file"),
            proxy=config.get("proxy"),
        )
        print("   Client created successfully!")

        # Example: Get track info
        track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
        print(f"\n7. Testing client with track: {track_url}")

        track = client.get_track_info(track_url)
        print(f"   Track: {track.get('name', 'Unknown')}")
        if track.get("artists"):
            print(f"   Artists: {', '.join(a['name'] for a in track['artists'])}")

    except Exception as e:
        print(f"   Error: {e}")

    # 8. Show current configuration
    print("\n8. Current configuration:")
    config_dict = config.as_dict()
    # Show first 10 items
    for i, (key, value) in enumerate(config_dict.items()):
        if i >= 10:
            print(f"   ... and {len(config_dict) - 10} more settings")
            break
        print(f"   {key}: {value}")

    # Clean up
    if config_file.exists():
        config_file.unlink()
        print(f"\n9. Cleaned up {config_file}")


def advanced_configuration_example():
    """Demonstrate advanced configuration scenarios."""

    print("\n\n=== Advanced Configuration Examples ===\n")

    # Scenario 1: Different configurations for different use cases
    configs = {
        "high_performance": {
            "browser_type": "requests",
            "cache_enabled": True,
            "cache_ttl": 172800,  # 48 hours
            "timeout": 60,
            "retries": 5,
            "rate_limit_requests": 20,
        },
        "low_bandwidth": {
            "browser_type": "requests",
            "timeout": 30,
            "retries": 2,
            "rate_limit_requests": 5,
            "rate_limit_period": 60,
        },
        "debugging": {
            "browser_type": "selenium",
            "log_level": "DEBUG",
            "debug": True,
            "cache_enabled": False,
            "timeout": 120,
        },
    }

    # Use different configurations based on context
    environment = os.getenv("SPOTIFY_SCRAPER_ENV", "production")

    if environment == "debug":
        config_dict = configs["debugging"]
    elif environment == "mobile":
        config_dict = configs["low_bandwidth"]
    else:
        config_dict = configs["high_performance"]

    config = Config(config_dict=config_dict)
    print(f"Using configuration for environment: {environment}")
    print(
        f"Configuration: {config.get('browser_type')} browser, "
        f"log level {config.get('log_level')}"
    )


if __name__ == "__main__":
    main()
    advanced_configuration_example()
