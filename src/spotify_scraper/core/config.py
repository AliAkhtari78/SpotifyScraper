"""
Configuration management for the SpotifyScraper package.

This module provides functionality for managing configuration options,
with support for default values, environment variables, and configuration files.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, cast

from spotify_scraper.core.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for SpotifyScraper.
    
    This class handles configuration options for the library, with support
    for default values, environment variables, and configuration files.
    
    Attributes:
        values: Dictionary of configuration values
        config_file: Path to configuration file
    """
    
    def __init__(
        self,
        config_file: Optional[Union[str, Path]] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        use_env: bool = True,
    ):
        """
        Initialize the Config instance.
        
        Args:
            config_file: Path to configuration file (optional)
            config_dict: Dictionary with configuration values (optional)
            use_env: Whether to use environment variables (default: True)
        """
        # Set default values
        self.values = {
            # General settings
            "debug": False,
            "log_level": "INFO",
            "log_file": None,
            
            # Network settings
            "timeout": 30,
            "retries": 3,
            "retry_delay": 1,
            "max_connections": 10,
            "user_agent": None,  # Will use default from constants
            
            # Authentication settings
            "auth_token": None,
            "refresh_token": None,
            "client_id": None,
            "client_secret": None,
            "auth_scope": "basic",
            "cookie_file": None,
            "credentials_dir": os.path.expanduser("~/.spotify-scraper"),
            
            # Browser settings
            "browser_type": "auto",
            "selenium_headless": True,
            "selenium_driver_path": None,
            "selenium_browser": "chrome",
            "selenium_arguments": [],
            
            # Proxy settings
            "proxy": None,
            
            # Cache settings
            "cache_enabled": True,
            "cache_ttl": 3600,  # 1 hour
            "cache_dir": os.path.expanduser("~/.spotify-scraper/cache"),
            "cache_size_limit": 100 * 1024 * 1024,  # 100 MB
            
            # Media settings
            "download_dir": os.path.expanduser("~/Downloads"),
            "audio_format": "mp3",
            "image_format": "jpg",
            "include_metadata": True,
            
            # Rate limiting
            "rate_limit_enabled": True,
            "rate_limit_requests": 10,
            "rate_limit_period": 60,  # 10 requests per minute
        }
        
        # Load configuration from file if provided
        self.config_file = None
        if config_file:
            self.config_file = Path(config_file)
            self._load_from_file()
        
        # Update with provided configuration dictionary
        if config_dict:
            self._update_from_dict(config_dict)
        
        # Update from environment variables if enabled
        if use_env:
            self._update_from_env()
        
        logger.debug(f"Configuration initialized with {len(self.values)} values")
    
    def _load_from_file(self) -> None:
        """
        Load configuration from file.
        
        Raises:
            ConfigurationError: If the file cannot be read or parsed
        """
        if not self.config_file or not self.config_file.exists():
            logger.debug(f"Configuration file not found: {self.config_file}")
            return
        
        try:
            with open(self.config_file, "r") as f:
                config_data = json.load(f)
                
            self._update_from_dict(config_data)
            logger.debug(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {self.config_file}: {e}")
            raise ConfigurationError(f"Failed to load configuration file: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
        """
        for key, value in config_dict.items():
            if key in self.values:
                self.values[key] = value
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def _update_from_env(self) -> None:
        """
        Update configuration from environment variables.
        
        Environment variables should be prefixed with SPOTIFY_SCRAPER_,
        e.g., SPOTIFY_SCRAPER_DEBUG=1
        """
        prefix = "SPOTIFY_SCRAPER_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                
                if config_key in self.values:
                    # Convert values to appropriate types
                    if isinstance(self.values[config_key], bool):
                        self.values[config_key] = value.lower() in ("1", "true", "yes", "y")
                    elif isinstance(self.values[config_key], int):
                        try:
                            self.values[config_key] = int(value)
                        except ValueError:
                            logger.warning(f"Invalid integer value for {key}: {value}")
                    elif isinstance(self.values[config_key], float):
                        try:
                            self.values[config_key] = float(value)
                        except ValueError:
                            logger.warning(f"Invalid float value for {key}: {value}")
                    elif isinstance(self.values[config_key], list):
                        self.values[config_key] = value.split(",")
                    else:
                        self.values[config_key] = value
                        
                    logger.debug(f"Set {config_key} from environment variable {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        return self.values.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Raises:
            ConfigurationError: If the key is not valid
        """
        if key in self.values:
            self.values[key] = value
            logger.debug(f"Set configuration value: {key}={value}")
        else:
            logger.error(f"Invalid configuration key: {key}")
            raise ConfigurationError(f"Invalid configuration key: {key}")
    
    def save(self, config_file: Optional[Union[str, Path]] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config_file: Path to configuration file (optional, uses self.config_file if not provided)
            
        Raises:
            ConfigurationError: If the file cannot be written
        """
        file_path = Path(config_file) if config_file else self.config_file
        
        if not file_path:
            logger.error("No configuration file specified")
            raise ConfigurationError("No configuration file specified")
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, "w") as f:
                json.dump(self.values, f, indent=2)
                
            logger.debug(f"Saved configuration to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {e}")
            raise ConfigurationError(f"Failed to save configuration file: {e}")
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
            
        Raises:
            KeyError: If the key is not found
        """
        if key in self.values:
            return self.values[key]
        else:
            raise KeyError(f"Invalid configuration key: {key}")
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Raises:
            ConfigurationError: If the key is not valid
        """
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a configuration key exists.
        
        Args:
            key: Configuration key
            
        Returns:
            True if the key exists, False otherwise
        """
        return key in self.values
    
    def __repr__(self) -> str:
        """
        Get string representation of the Config instance.
        
        Returns:
            String representation
        """
        return f"Config({len(self.values)} values)"
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Dictionary with configuration values
        """
        return dict(self.values)
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> "Config":
        """
        Create Config instance from file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Config instance
            
        Raises:
            ConfigurationError: If the file cannot be read or parsed
        """
        return cls(config_file=config_file)
