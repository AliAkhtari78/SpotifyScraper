#!/usr/bin/env python3
"""
Configuration management system for SpotifyScraper.

This module provides a comprehensive configuration management system that handles:
- Environment-based configuration
- Configuration file loading (JSON, YAML, TOML)
- Default values and validation
- Dynamic configuration updates
- Secure credential storage

Author: SpotifyScraper Development Team
Date: 2025-01-22
Version: 2.0.0
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
import configparser
from abc import ABC, abstractmethod

# Optional imports for additional format support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Enumeration of available browser types."""
    REQUESTS = "requests"
    SELENIUM = "selenium"
    AUTO = "auto"


class LogLevel(Enum):
    """Enumeration of logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ConfigFormat(Enum):
    """Enumeration of configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    ENV = "env"


@dataclass
class ProxyConfig:
    """Proxy configuration settings."""
    http: Optional[str] = None
    https: Optional[str] = None
    no_proxy: Optional[List[str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proxy config to dictionary format."""
        result = {}
        if self.http:
            result['http'] = self.http
        if self.https:
            result['https'] = self.https
        return result


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    enabled: bool = True
    directory: Optional[str] = None
    ttl_hours: int = 24
    max_size_mb: int = 500
    
    def __post_init__(self):
        """Initialize cache directory if not specified."""
        if self.directory is None:
            self.directory = str(Path.home() / ".spotify_scraper_cache")


@dataclass
class RetryConfig:
    """Retry configuration settings."""
    max_attempts: int = 3
    delay_seconds: float = 1.0
    exponential_backoff: bool = True
    retry_on_errors: List[str] = field(default_factory=lambda: ["NetworkError", "ScrapingError"])


@dataclass
class MediaConfig:
    """Media download configuration settings."""
    audio_quality: str = "high"  # high, medium, low
    audio_format: str = "mp3"
    cover_quality: str = "large"  # large, medium, small
    embed_metadata: bool = True
    organize_by_artist: bool = False
    sanitize_filenames: bool = True


@dataclass
class AuthConfig:
    """Authentication configuration settings."""
    cookie_file: Optional[str] = None
    cookies: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    user_agent: Optional[str] = None
    session_file: Optional[str] = None
    auto_refresh: bool = True


@dataclass
class SpotifyScraperConfig:
    """
    Main configuration class for SpotifyScraper.
    
    This dataclass holds all configuration settings for the SpotifyScraper
    library, providing a centralized way to manage settings.
    """
    # Core settings
    browser_type: BrowserType = BrowserType.REQUESTS
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    
    # Sub-configurations
    auth: AuthConfig = field(default_factory=AuthConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    media: MediaConfig = field(default_factory=MediaConfig)
    
    # Output settings
    output_directory: str = field(default_factory=lambda: str(Path.cwd()))
    create_output_dirs: bool = True
    
    # Advanced settings
    timeout_seconds: int = 30
    max_concurrent_requests: int = 5
    rate_limit_delay: float = 0.5
    debug_mode: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = asdict(self)
        
        # Convert enums to strings
        result['browser_type'] = self.browser_type.value
        result['log_level'] = self.log_level.value
        
        # Convert proxy config
        result['proxy'] = self.proxy.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpotifyScraperConfig':
        """Create configuration from dictionary."""
        # Convert string values to enums
        if 'browser_type' in data and isinstance(data['browser_type'], str):
            data['browser_type'] = BrowserType(data['browser_type'])
        
        if 'log_level' in data and isinstance(data['log_level'], str):
            data['log_level'] = LogLevel(data['log_level'])
        
        # Convert nested configurations
        if 'auth' in data and isinstance(data['auth'], dict):
            data['auth'] = AuthConfig(**data['auth'])
        
        if 'proxy' in data and isinstance(data['proxy'], dict):
            data['proxy'] = ProxyConfig(**data['proxy'])
        
        if 'cache' in data and isinstance(data['cache'], dict):
            data['cache'] = CacheConfig(**data['cache'])
        
        if 'retry' in data and isinstance(data['retry'], dict):
            data['retry'] = RetryConfig(**data['retry'])
        
        if 'media' in data and isinstance(data['media'], dict):
            data['media'] = MediaConfig(**data['media'])
        
        return cls(**data)
    
    def validate(self) -> List[str]:
        """
        Validate configuration settings.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate paths
        if self.auth.cookie_file and not Path(self.auth.cookie_file).exists():
            errors.append(f"Cookie file not found: {self.auth.cookie_file}")
        
        if self.auth.session_file and not Path(self.auth.session_file).parent.exists():
            errors.append(f"Session file directory not found: {Path(self.auth.session_file).parent}")
        
        # Validate numeric ranges
        if self.retry.max_attempts < 1:
            errors.append("max_attempts must be at least 1")
        
        if self.retry.delay_seconds < 0:
            errors.append("delay_seconds must be non-negative")
        
        if self.timeout_seconds < 1:
            errors.append("timeout_seconds must be at least 1")
        
        if self.cache.ttl_hours < 1:
            errors.append("cache.ttl_hours must be at least 1")
        
        # Validate media settings
        valid_audio_qualities = ["high", "medium", "low"]
        if self.media.audio_quality not in valid_audio_qualities:
            errors.append(f"audio_quality must be one of: {valid_audio_qualities}")
        
        valid_cover_qualities = ["large", "medium", "small"]
        if self.media.cover_quality not in valid_cover_qualities:
            errors.append(f"cover_quality must be one of: {valid_cover_qualities}")
        
        return errors


class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""
    
    @abstractmethod
    def load(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from file."""
        pass
    
    @abstractmethod
    def save(self, config: Dict[str, Any], path: Union[str, Path]) -> None:
        """Save configuration to file."""
        pass


class JSONConfigLoader(ConfigLoader):
    """JSON configuration file loader."""
    
    def load(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, config: Dict[str, Any], path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class YAMLConfigLoader(ConfigLoader):
    """YAML configuration file loader."""
    
    def __init__(self):
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML configuration support")
    
    def load(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save(self, config: Dict[str, Any], path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)


class TOMLConfigLoader(ConfigLoader):
    """TOML configuration file loader."""
    
    def __init__(self):
        if not TOML_AVAILABLE:
            raise ImportError("toml is required for TOML configuration support")
    
    def load(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        with open(path, 'r', encoding='utf-8') as f:
            return toml.load(f)
    
    def save(self, config: Dict[str, Any], path: Union[str, Path]) -> None:
        """Save configuration to TOML file."""
        with open(path, 'w', encoding='utf-8') as f:
            toml.dump(config, f)


class INIConfigLoader(ConfigLoader):
    """INI configuration file loader."""
    
    def load(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from INI file."""
        parser = configparser.ConfigParser()
        parser.read(path)
        
        # Convert to nested dictionary
        result = {}
        for section in parser.sections():
            result[section] = dict(parser.items(section))
        
        # Convert string values to appropriate types
        return self._convert_types(result)
    
    def save(self, config: Dict[str, Any], path: Union[str, Path]) -> None:
        """Save configuration to INI file."""
        parser = configparser.ConfigParser()
        
        # Flatten nested configuration
        for section, values in config.items():
            if isinstance(values, dict):
                parser.add_section(section)
                for key, value in values.items():
                    parser.set(section, key, str(value))
        
        with open(path, 'w', encoding='utf-8') as f:
            parser.write(f)
    
    def _convert_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert string values to appropriate types."""
        result = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._convert_types(value)
            elif isinstance(value, str):
                # Try to convert to appropriate type
                if value.lower() in ('true', 'false'):
                    result[key] = value.lower() == 'true'
                elif value.isdigit():
                    result[key] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    result[key] = float(value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result


class EnvironmentConfigLoader(ConfigLoader):
    """Environment variable configuration loader."""
    
    def __init__(self, prefix: str = "SPOTIFY_SCRAPER_"):
        self.prefix = prefix
    
    def load(self, path: Union[str, Path] = None) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                # Remove prefix and convert to nested structure
                config_key = key[len(self.prefix):].lower()
                
                # Handle nested keys (e.g., SPOTIFY_SCRAPER_AUTH_COOKIE_FILE)
                parts = config_key.split('_')
                current = config
                
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Convert value types
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
                
                current[parts[-1]] = value
        
        return config
    
    def save(self, config: Dict[str, Any], path: Union[str, Path] = None) -> None:
        """Save configuration to .env file."""
        if path is None:
            path = Path.cwd() / ".env"
        
        lines = []
        self._flatten_config(config, self.prefix, lines)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _flatten_config(self, config: Dict[str, Any], prefix: str, lines: List[str]) -> None:
        """Flatten nested configuration to environment variable format."""
        for key, value in config.items():
            env_key = f"{prefix}{key.upper()}"
            
            if isinstance(value, dict):
                self._flatten_config(value, f"{env_key}_", lines)
            else:
                lines.append(f"{env_key}={value}")


class ConfigurationManager:
    """
    Main configuration manager for SpotifyScraper.
    
    This class provides a unified interface for managing configuration from
    multiple sources including files, environment variables, and runtime updates.
    """
    
    # Default configuration file locations
    DEFAULT_CONFIG_PATHS = [
        Path.home() / ".spotify_scraper" / "config.json",
        Path.home() / ".config" / "spotify_scraper" / "config.json",
        Path.cwd() / "spotify_scraper.json",
        Path.cwd() / ".spotify_scraper.json"
    ]
    
    def __init__(self, config: Optional[SpotifyScraperConfig] = None):
        """
        Initialize configuration manager.
        
        Args:
            config: Initial configuration (creates default if None)
        """
        self.config = config or SpotifyScraperConfig()
        self._loaders = {
            ConfigFormat.JSON: JSONConfigLoader(),
            ConfigFormat.ENV: EnvironmentConfigLoader()
        }
        
        # Add optional loaders
        if YAML_AVAILABLE:
            self._loaders[ConfigFormat.YAML] = YAMLConfigLoader()
        
        if TOML_AVAILABLE:
            self._loaders[ConfigFormat.TOML] = TOMLConfigLoader()
        
        self._loaders[ConfigFormat.INI] = INIConfigLoader()
        
        # Load configuration from various sources
        self._load_from_defaults()
        self._load_from_environment()
    
    def _load_from_defaults(self) -> None:
        """Load configuration from default file locations."""
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                try:
                    self.load_from_file(path)
                    logger.info(f"Loaded configuration from: {path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load config from {path}: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_config = self._loaders[ConfigFormat.ENV].load(None)
        if env_config:
            self.update(env_config)
            logger.debug("Loaded configuration from environment variables")
    
    def load_from_file(self, path: Union[str, Path], format: Optional[ConfigFormat] = None) -> None:
        """
        Load configuration from file.
        
        Args:
            path: Path to configuration file
            format: File format (auto-detected if None)
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        # Auto-detect format from extension
        if format is None:
            ext = path.suffix.lower().lstrip('.')
            try:
                format = ConfigFormat(ext)
            except ValueError:
                raise ValueError(f"Unknown configuration format: {ext}")
        
        # Check if loader is available
        if format not in self._loaders:
            raise ValueError(f"Configuration format not supported: {format.value}")
        
        # Load configuration
        loader = self._loaders[format]
        data = loader.load(path)
        
        # Update configuration
        self.config = SpotifyScraperConfig.from_dict(data)
    
    def save_to_file(self, path: Union[str, Path], format: Optional[ConfigFormat] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            path: Path to save configuration
            format: File format (auto-detected if None)
        """
        path = Path(path)
        
        # Auto-detect format from extension
        if format is None:
            ext = path.suffix.lower().lstrip('.')
            try:
                format = ConfigFormat(ext)
            except ValueError:
                # Default to JSON
                format = ConfigFormat.JSON
                path = path.with_suffix('.json')
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if loader is available
        if format not in self._loaders:
            raise ValueError(f"Configuration format not supported: {format.value}")
        
        # Save configuration
        loader = self._loaders[format]
        loader.save(self.config.to_dict(), path)
        
        logger.info(f"Saved configuration to: {path}")
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        current_dict = self.config.to_dict()
        updated_dict = self._deep_merge(current_dict, updates)
        self.config = SpotifyScraperConfig.from_dict(updated_dict)
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            updates: Updates to apply
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate(self) -> List[str]:
        """
        Validate current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        return self.config.validate()
    
    def get_client_kwargs(self) -> Dict[str, Any]:
        """
        Get keyword arguments for SpotifyClient initialization.
        
        Returns:
            Dictionary of client initialization parameters
        """
        return {
            'cookie_file': self.config.auth.cookie_file,
            'cookies': self.config.auth.cookies,
            'headers': self.config.auth.headers,
            'proxy': self.config.proxy.to_dict(),
            'browser_type': self.config.browser_type.value,
            'log_level': self.config.log_level.value,
            'log_file': self.config.log_file
        }
    
    def create_client(self) -> 'SpotifyClient':
        """
        Create a SpotifyClient instance with current configuration.
        
        Returns:
            Configured SpotifyClient instance
        """
        from spotify_scraper import SpotifyClient
        return SpotifyClient(**self.get_client_kwargs())
    
    def get_profile(self, profile_name: str) -> Optional[SpotifyScraperConfig]:
        """
        Get a named configuration profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Configuration profile or None if not found
        """
        profile_path = Path.home() / ".spotify_scraper" / "profiles" / f"{profile_name}.json"
        
        if profile_path.exists():
            try:
                loader = self._loaders[ConfigFormat.JSON]
                data = loader.load(profile_path)
                return SpotifyScraperConfig.from_dict(data)
            except Exception as e:
                logger.error(f"Failed to load profile {profile_name}: {e}")
        
        return None
    
    def save_profile(self, profile_name: str, config: Optional[SpotifyScraperConfig] = None) -> None:
        """
        Save a named configuration profile.
        
        Args:
            profile_name: Name of the profile
            config: Configuration to save (uses current if None)
        """
        config = config or self.config
        profile_dir = Path.home() / ".spotify_scraper" / "profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        profile_path = profile_dir / f"{profile_name}.json"
        
        loader = self._loaders[ConfigFormat.JSON]
        loader.save(config.to_dict(), profile_path)
        
        logger.info(f"Saved profile: {profile_name}")
    
    def list_profiles(self) -> List[str]:
        """
        List available configuration profiles.
        
        Returns:
            List of profile names
        """
        profile_dir = Path.home() / ".spotify_scraper" / "profiles"
        
        if not profile_dir.exists():
            return []
        
        return [p.stem for p in profile_dir.glob("*.json")]


# Convenience functions

def load_config(path: Optional[Union[str, Path]] = None) -> SpotifyScraperConfig:
    """
    Load configuration from file or defaults.
    
    Args:
        path: Optional path to configuration file
        
    Returns:
        Loaded configuration
    """
    manager = ConfigurationManager()
    
    if path:
        manager.load_from_file(path)
    
    return manager.config


def create_default_config(path: Union[str, Path], format: ConfigFormat = ConfigFormat.JSON) -> None:
    """
    Create a default configuration file.
    
    Args:
        path: Path to save configuration
        format: Configuration format
    """
    manager = ConfigurationManager()
    manager.save_to_file(path, format)


# Example configuration files

EXAMPLE_JSON_CONFIG = """
{
  "browser_type": "requests",
  "log_level": "INFO",
  "auth": {
    "cookie_file": "~/.spotify_scraper/cookies.txt",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  },
  "cache": {
    "enabled": true,
    "directory": "~/.spotify_scraper/cache",
    "ttl_hours": 24
  },
  "retry": {
    "max_attempts": 3,
    "delay_seconds": 1.0,
    "exponential_backoff": true
  },
  "media": {
    "audio_quality": "high",
    "cover_quality": "large",
    "embed_metadata": true
  }
}
"""

EXAMPLE_YAML_CONFIG = """
browser_type: requests
log_level: INFO

auth:
  cookie_file: ~/.spotify_scraper/cookies.txt
  user_agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

cache:
  enabled: true
  directory: ~/.spotify_scraper/cache
  ttl_hours: 24

retry:
  max_attempts: 3
  delay_seconds: 1.0
  exponential_backoff: true

media:
  audio_quality: high
  cover_quality: large
  embed_metadata: true
"""


if __name__ == "__main__":
    # Example usage
    # Create configuration manager
    manager = ConfigurationManager()
    
    # Update configuration
    manager.update({
        "log_level": "DEBUG",
        "cache": {
            "ttl_hours": 48
        }
    })
    
    # Validate configuration
    errors = manager.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid")
    
    # Save configuration
    manager.save_to_file("spotify_scraper_config.json")
    
    # Create client with configuration
    client = manager.create_client()
    print(f"Created client with browser type: {manager.config.browser_type.value}")