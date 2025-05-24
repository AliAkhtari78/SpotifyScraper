"""Tests for core.config module."""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from spotify_scraper.core.config import Config


class TestConfig:
    """Test Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        # Check default values
        assert config.cache_enabled is True
        assert config.cache_dir == ".cache"
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.proxy is None
        assert config.user_agent.startswith("Mozilla/5.0")
        assert config.rate_limit == 1.0
        assert config.cookie_file is None
        assert config.session_file is None
        assert config.log_level == "INFO"
        assert config.log_file is None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = Config(
            cache_enabled=False,
            cache_dir="/tmp/cache",
            max_retries=5,
            timeout=60,
            proxy="http://proxy.example.com:8080",
            user_agent="CustomAgent/1.0",
            rate_limit=0.5,
            cookie_file="cookies.txt",
            session_file="session.json",
            log_level="DEBUG",
            log_file="app.log"
        )
        
        assert config.cache_enabled is False
        assert config.cache_dir == "/tmp/cache"
        assert config.max_retries == 5
        assert config.timeout == 60
        assert config.proxy == "http://proxy.example.com:8080"
        assert config.user_agent == "CustomAgent/1.0"
        assert config.rate_limit == 0.5
        assert config.cookie_file == "cookies.txt"
        assert config.session_file == "session.json"
        assert config.log_level == "DEBUG"
        assert config.log_file == "app.log"

    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "cache_enabled": False,
            "cache_dir": "/custom/cache",
            "max_retries": 10,
            "timeout": 120,
            "proxy": "socks5://localhost:9050",
            "user_agent": "TestAgent/2.0",
            "rate_limit": 2.0,
            "cookie_file": "test_cookies.txt",
            "session_file": "test_session.json",
            "log_level": "WARNING",
            "log_file": "test.log"
        }
        
        config = Config.from_dict(config_dict)
        
        assert config.cache_enabled is False
        assert config.cache_dir == "/custom/cache"
        assert config.max_retries == 10
        assert config.timeout == 120
        assert config.proxy == "socks5://localhost:9050"
        assert config.user_agent == "TestAgent/2.0"
        assert config.rate_limit == 2.0
        assert config.cookie_file == "test_cookies.txt"
        assert config.session_file == "test_session.json"
        assert config.log_level == "WARNING"
        assert config.log_file == "test.log"

    def test_from_dict_partial(self):
        """Test creating config from partial dictionary."""
        config_dict = {
            "cache_enabled": False,
            "max_retries": 7
        }
        
        config = Config.from_dict(config_dict)
        
        # Changed values
        assert config.cache_enabled is False
        assert config.max_retries == 7
        
        # Default values
        assert config.cache_dir == ".cache"
        assert config.timeout == 30
        assert config.proxy is None

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            cache_enabled=False,
            max_retries=5,
            proxy="http://proxy.example.com:8080"
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["cache_enabled"] is False
        assert config_dict["max_retries"] == 5
        assert config_dict["proxy"] == "http://proxy.example.com:8080"
        assert config_dict["cache_dir"] == ".cache"  # Default value

    def test_from_file_json(self):
        """Test loading config from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "cache_enabled": False,
                "max_retries": 8,
                "timeout": 90
            }, f)
            temp_file = f.name
        
        try:
            config = Config.from_file(temp_file)
            
            assert config.cache_enabled is False
            assert config.max_retries == 8
            assert config.timeout == 90
        finally:
            os.unlink(temp_file)

    def test_from_file_not_found(self):
        """Test loading config from non-existent file."""
        with pytest.raises(FileNotFoundError):
            Config.from_file("non_existent_file.json")

    def test_from_file_invalid_json(self):
        """Test loading config from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                Config.from_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_save_json(self):
        """Test saving config to JSON file."""
        config = Config(
            cache_enabled=False,
            max_retries=5,
            timeout=45
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            config.save(temp_file)
            
            # Load and verify
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["cache_enabled"] is False
            assert saved_data["max_retries"] == 5
            assert saved_data["timeout"] == 45
        finally:
            os.unlink(temp_file)

    def test_save_creates_directory(self):
        """Test save creates parent directory if needed."""
        config = Config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "config.json"
            
            config.save(str(file_path))
            
            assert file_path.exists()
            assert file_path.parent.exists()

    def test_validate_valid_config(self):
        """Test validating a valid configuration."""
        config = Config()
        errors = config.validate()
        
        assert len(errors) == 0

    def test_validate_invalid_values(self):
        """Test validating configuration with invalid values."""
        # Test with invalid max_retries
        config = Config(max_retries=-1)
        errors = config.validate()
        assert any("max_retries must be positive" in error for error in errors)
        
        # Test with invalid timeout
        config = Config(timeout=0)
        errors = config.validate()
        assert any("timeout must be positive" in error for error in errors)
        
        # Test with invalid rate_limit
        config = Config(rate_limit=-0.5)
        errors = config.validate()
        assert any("rate_limit must be non-negative" in error for error in errors)

    def test_validate_invalid_paths(self):
        """Test validating configuration with invalid paths."""
        # Test with non-existent cookie file
        config = Config(cookie_file="/non/existent/cookies.txt")
        errors = config.validate()
        assert any("cookie_file does not exist" in error for error in errors)

    def test_validate_invalid_log_level(self):
        """Test validating configuration with invalid log level."""
        config = Config(log_level="INVALID")
        errors = config.validate()
        assert any("Invalid log_level" in error for error in errors)

    def test_merge(self):
        """Test merging configurations."""
        config1 = Config(
            cache_enabled=True,
            max_retries=3,
            timeout=30
        )
        
        config2 = Config(
            cache_enabled=False,
            max_retries=5,
            proxy="http://proxy.example.com:8080"
        )
        
        merged = config1.merge(config2)
        
        # Values from config2 should override config1
        assert merged.cache_enabled is False
        assert merged.max_retries == 5
        assert merged.proxy == "http://proxy.example.com:8080"
        
        # Other values from config1 should remain
        assert merged.timeout == 30

    def test_merge_none_values(self):
        """Test merging with None values doesn't override."""
        config1 = Config(
            cache_enabled=True,
            proxy="http://proxy1.example.com:8080"
        )
        
        config2 = Config()  # All defaults, proxy is None
        
        merged = config1.merge(config2)
        
        # Original values should be preserved
        assert merged.cache_enabled is True
        assert merged.proxy == "http://proxy1.example.com:8080"

    @mock.patch.dict(os.environ, {
        "SPOTIFY_CACHE_ENABLED": "false",
        "SPOTIFY_MAX_RETRIES": "10",
        "SPOTIFY_TIMEOUT": "120",
        "SPOTIFY_PROXY": "http://env-proxy.example.com:3128",
        "SPOTIFY_USER_AGENT": "EnvAgent/1.0",
        "SPOTIFY_RATE_LIMIT": "0.25",
        "SPOTIFY_COOKIE_FILE": "env_cookies.txt",
        "SPOTIFY_SESSION_FILE": "env_session.json",
        "SPOTIFY_LOG_LEVEL": "ERROR",
        "SPOTIFY_LOG_FILE": "env.log"
    })
    def test_from_env(self):
        """Test loading config from environment variables."""
        config = Config.from_env()
        
        assert config.cache_enabled is False
        assert config.max_retries == 10
        assert config.timeout == 120
        assert config.proxy == "http://env-proxy.example.com:3128"
        assert config.user_agent == "EnvAgent/1.0"
        assert config.rate_limit == 0.25
        assert config.cookie_file == "env_cookies.txt"
        assert config.session_file == "env_session.json"
        assert config.log_level == "ERROR"
        assert config.log_file == "env.log"

    @mock.patch.dict(os.environ, {
        "SPOTIFY_CACHE_ENABLED": "invalid_bool",
        "SPOTIFY_MAX_RETRIES": "not_a_number",
        "SPOTIFY_TIMEOUT": "also_not_a_number",
        "SPOTIFY_RATE_LIMIT": "invalid_float"
    })
    def test_from_env_invalid_values(self):
        """Test loading config from environment with invalid values."""
        config = Config.from_env()
        
        # Should use defaults for invalid values
        assert config.cache_enabled is True  # Default
        assert config.max_retries == 3  # Default
        assert config.timeout == 30  # Default
        assert config.rate_limit == 1.0  # Default

    def test_repr(self):
        """Test string representation of config."""
        config = Config(
            cache_enabled=False,
            max_retries=5
        )
        
        repr_str = repr(config)
        assert "Config" in repr_str
        assert "cache_enabled=False" in repr_str
        assert "max_retries=5" in repr_str