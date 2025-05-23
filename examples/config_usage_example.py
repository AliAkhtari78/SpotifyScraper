#!/usr/bin/env python3
"""
Example demonstrating configuration management with SpotifyScraper.

This example shows how to use the configuration management system to:
- Load configuration from files
- Update configuration programmatically
- Create different client configurations
- Save and load configuration profiles
"""

from pathlib import Path
import json

from spotify_scraper import SpotifyClient
from spotify_scraper.config_manager import (
    ConfigurationManager,
    SpotifyScraperConfig,
    BrowserType,
    LogLevel,
    ConfigFormat
)


def main():
    """Demonstrate configuration management features."""
    
    print("=== SpotifyScraper Configuration Management Example ===\n")
    
    # 1. Create default configuration
    print("1. Creating default configuration...")
    manager = ConfigurationManager()
    print(f"   Browser type: {manager.config.browser_type.value}")
    print(f"   Log level: {manager.config.log_level.value}")
    print(f"   Cache enabled: {manager.config.cache.enabled}")
    
    # 2. Load configuration from file
    print("\n2. Loading configuration from file...")
    config_file = Path("examples/config_example.json")
    if config_file.exists():
        manager.load_from_file(config_file)
        print("   Configuration loaded successfully")
        print(f"   Output directory: {manager.config.output_directory}")
        print(f"   Cache directory: {manager.config.cache.directory}")
    
    # 3. Update configuration programmatically
    print("\n3. Updating configuration...")
    manager.update({
        "log_level": "DEBUG",
        "cache": {
            "ttl_hours": 48,
            "enabled": True
        },
        "media": {
            "audio_quality": "medium"
        }
    })
    print(f"   Updated log level: {manager.config.log_level.value}")
    print(f"   Updated cache TTL: {manager.config.cache.ttl_hours} hours")
    print(f"   Updated audio quality: {manager.config.media.audio_quality}")
    
    # 4. Validate configuration
    print("\n4. Validating configuration...")
    errors = manager.validate()
    if errors:
        print("   Validation errors found:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("   Configuration is valid!")
    
    # 5. Save configuration profile
    print("\n5. Saving configuration profiles...")
    manager.save_profile("high_quality")
    
    # Create and save a low-quality profile
    low_quality_config = SpotifyScraperConfig(
        browser_type=BrowserType.REQUESTS,
        log_level=LogLevel.WARNING,
        media=manager.config.media
    )
    low_quality_config.media.audio_quality = "low"
    low_quality_config.media.cover_quality = "small"
    
    manager_low = ConfigurationManager(low_quality_config)
    manager_low.save_profile("low_quality")
    
    print("   Saved profiles: high_quality, low_quality")
    
    # 6. List available profiles
    print("\n6. Available configuration profiles:")
    profiles = manager.list_profiles()
    for profile in profiles:
        print(f"   - {profile}")
    
    # 7. Create client with configuration
    print("\n7. Creating SpotifyClient with configuration...")
    try:
        client = manager.create_client()
        print("   Client created successfully!")
        
        # Example: Get track info with configured client
        track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
        print(f"\n8. Testing client with track: {track_url}")
        
        track_info = client.get_track_info(track_url)
        print(f"   Track: {track_info['name']}")
        print(f"   Artists: {', '.join(a['name'] for a in track_info['artists'])}")
        
        client.close()
        
    except Exception as e:
        print(f"   Error creating client: {e}")
    
    # 9. Environment variable configuration
    print("\n9. Environment variable configuration example:")
    print("   You can set environment variables like:")
    print("   export SPOTIFY_SCRAPER_LOG_LEVEL=DEBUG")
    print("   export SPOTIFY_SCRAPER_CACHE_ENABLED=true")
    print("   export SPOTIFY_SCRAPER_AUTH_COOKIE_FILE=~/.spotify_cookies.txt")
    
    # 10. Export configuration examples
    print("\n10. Exporting configuration to different formats...")
    
    # Save as JSON
    manager.save_to_file("spotify_config.json", ConfigFormat.JSON)
    print("   Saved as JSON: spotify_config.json")
    
    # Save as environment variables
    manager.save_to_file(".env", ConfigFormat.ENV)
    print("   Saved as .env file")
    
    # Pretty print current configuration
    print("\n11. Current configuration:")
    config_dict = manager.config.to_dict()
    print(json.dumps(config_dict, indent=2))


def advanced_configuration_example():
    """Demonstrate advanced configuration scenarios."""
    
    print("\n=== Advanced Configuration Examples ===\n")
    
    # Scenario 1: Different configurations for different use cases
    configs = {
        "high_performance": SpotifyScraperConfig(
            browser_type=BrowserType.REQUESTS,
            cache=CacheConfig(enabled=True, ttl_hours=48),
            retry=RetryConfig(max_attempts=5, exponential_backoff=True),
            timeout_seconds=60,
            max_concurrent_requests=10
        ),
        
        "low_bandwidth": SpotifyScraperConfig(
            browser_type=BrowserType.REQUESTS,
            media=MediaConfig(
                audio_quality="low",
                cover_quality="small",
                embed_metadata=False
            ),
            rate_limit_delay=2.0,
            max_concurrent_requests=2
        ),
        
        "debugging": SpotifyScraperConfig(
            browser_type=BrowserType.SELENIUM,
            log_level=LogLevel.DEBUG,
            debug_mode=True,
            cache=CacheConfig(enabled=False),
            timeout_seconds=120
        )
    }
    
    # Use different configurations based on context
    import os
    environment = os.getenv("SPOTIFY_SCRAPER_ENV", "production")
    
    if environment == "debug":
        config = configs["debugging"]
    elif environment == "mobile":
        config = configs["low_bandwidth"]
    else:
        config = configs["high_performance"]
    
    print(f"Using configuration for environment: {environment}")
    print(f"Configuration: {config.browser_type.value} browser, "
          f"log level {config.log_level.value}")


def configuration_migration_example():
    """Example of migrating from old configuration format."""
    
    print("\n=== Configuration Migration Example ===\n")
    
    # Old configuration format (v1.x)
    old_config = {
        "browser": "chrome",
        "headless": True,
        "cookies_file": "/path/to/cookies.txt",
        "output_folder": "./downloads",
        "retry_count": 3
    }
    
    # Migrate to new format
    new_config = {
        "browser_type": "selenium" if old_config["browser"] != "requests" else "requests",
        "auth": {
            "cookie_file": old_config.get("cookies_file")
        },
        "output_directory": old_config.get("output_folder", "./output"),
        "retry": {
            "max_attempts": old_config.get("retry_count", 3)
        }
    }
    
    # Create configuration from migrated data
    manager = ConfigurationManager()
    manager.update(new_config)
    
    print("Migrated configuration:")
    print(f"  Browser: {old_config['browser']} -> {manager.config.browser_type.value}")
    print(f"  Cookies: {old_config['cookies_file']} -> {manager.config.auth.cookie_file}")
    print(f"  Output: {old_config['output_folder']} -> {manager.config.output_directory}")


if __name__ == "__main__":
    # Import required classes for advanced examples
    from spotify_scraper.config_manager import (
        CacheConfig, RetryConfig, MediaConfig
    )
    
    # Run examples
    main()
    advanced_configuration_example()
    configuration_migration_example()