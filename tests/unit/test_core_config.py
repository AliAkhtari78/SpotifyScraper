"""Tests for core.config module."""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from spotify_scraper.core.config import Config
from spotify_scraper.core.exceptions import ConfigurationError


class TestConfig:
    """Test Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        # Check default values from self.values
        assert config.get("cache_enabled") is True
        assert config.get("cache_dir") == os.path.expanduser("~/.spotify-scraper/cache")
        assert config.get("retries") == 3
        assert config.get("timeout") == 30
        assert config.get("proxy") is None
        assert config.get("user_agent") is None
        assert config.get("rate_limit_enabled") is True
        assert config.get("cookie_file") is None
        assert config.get("log_level") == "INFO"
        assert config.get("log_file") is None

    def test_custom_config_from_dict(self):
        """Test custom configuration values from dictionary."""
        config_dict = {
            "cache_enabled": False,
            "cache_dir": "/tmp/cache",
            "retries": 5,
            "timeout": 60,
            "proxy": "http://proxy.example.com:8080",
            "user_agent": "CustomAgent/1.0",
            "rate_limit_enabled": False,
            "cookie_file": "cookies.txt",
            "log_level": "DEBUG",
            "log_file": "app.log",
        }

        config = Config(config_dict=config_dict)

        assert config.get("cache_enabled") is False
        assert config.get("cache_dir") == "/tmp/cache"
        assert config.get("retries") == 5
        assert config.get("timeout") == 60
        assert config.get("proxy") == "http://proxy.example.com:8080"
        assert config.get("user_agent") == "CustomAgent/1.0"
        assert config.get("rate_limit_enabled") is False
        assert config.get("cookie_file") == "cookies.txt"
        assert config.get("log_level") == "DEBUG"
        assert config.get("log_file") == "app.log"

    def test_get_method(self):
        """Test get method with default values."""
        config = Config()

        # Existing key
        assert config.get("timeout") == 30

        # Non-existing key with default
        assert config.get("non_existent", "default") == "default"

        # Non-existing key without default
        assert config.get("non_existent") is None

    def test_set_method(self):
        """Test set method."""
        config = Config()

        # Set existing key
        config.set("timeout", 60)
        assert config.get("timeout") == 60

        # Try to set non-existing key
        with pytest.raises(ConfigurationError):
            config.set("non_existent", "value")

    def test_dict_access(self):
        """Test dictionary-style access."""
        config = Config()

        # __getitem__
        assert config["timeout"] == 30

        # __setitem__
        config["timeout"] = 60
        assert config["timeout"] == 60

        # __contains__
        assert "timeout" in config
        assert "non_existent" not in config

        # KeyError for non-existing key
        with pytest.raises(KeyError):
            _ = config["non_existent"]

    def test_as_dict(self):
        """Test converting config to dictionary."""
        config = Config(config_dict={"timeout": 60, "retries": 5})

        config_dict = config.as_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["timeout"] == 60
        assert config_dict["retries"] == 5
        assert config_dict["cache_enabled"] is True  # Default value

    def test_from_file_json(self):
        """Test loading config from JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"cache_enabled": False, "retries": 8, "timeout": 90}, f)
            temp_file = f.name

        try:
            config = Config.from_file(temp_file)

            assert config.get("cache_enabled") is False
            assert config.get("retries") == 8
            assert config.get("timeout") == 90
        finally:
            os.unlink(temp_file)

    def test_from_file_not_found(self):
        """Test loading config from non-existent file."""
        # Config should handle non-existent file gracefully
        config = Config(config_file="non_existent_file.json")

        # Should have default values
        assert config.get("timeout") == 30

    def test_from_file_invalid_json(self):
        """Test loading config from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            with pytest.raises(ConfigurationError):
                Config(config_file=temp_file)
        finally:
            os.unlink(temp_file)

    def test_save_json(self):
        """Test saving config to JSON file."""
        config = Config(config_dict={"cache_enabled": False, "retries": 5, "timeout": 45})

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            config.save(temp_file)

            # Load and verify
            with open(temp_file, "r") as f:
                saved_data = json.load(f)

            assert saved_data["cache_enabled"] is False
            assert saved_data["retries"] == 5
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

    def test_save_no_file_specified(self):
        """Test save without file path."""
        config = Config()

        with pytest.raises(ConfigurationError) as exc_info:
            config.save()

        assert "No configuration file specified" in str(exc_info.value)

    @mock.patch.dict(
        os.environ,
        {
            "SPOTIFY_SCRAPER_CACHE_ENABLED": "false",
            "SPOTIFY_SCRAPER_RETRIES": "10",
            "SPOTIFY_SCRAPER_TIMEOUT": "120",
            "SPOTIFY_SCRAPER_PROXY": "http://env-proxy.example.com:3128",
            "SPOTIFY_SCRAPER_USER_AGENT": "EnvAgent/1.0",
            "SPOTIFY_SCRAPER_RATE_LIMIT_ENABLED": "0",
            "SPOTIFY_SCRAPER_COOKIE_FILE": "env_cookies.txt",
            "SPOTIFY_SCRAPER_LOG_LEVEL": "ERROR",
            "SPOTIFY_SCRAPER_LOG_FILE": "env.log",
        },
    )
    def test_from_env(self):
        """Test loading config from environment variables."""
        config = Config(use_env=True)

        assert config.get("cache_enabled") is False
        assert config.get("retries") == 10
        assert config.get("timeout") == 120
        assert config.get("proxy") == "http://env-proxy.example.com:3128"
        assert config.get("user_agent") == "EnvAgent/1.0"
        assert config.get("rate_limit_enabled") is False
        assert config.get("cookie_file") == "env_cookies.txt"
        assert config.get("log_level") == "ERROR"
        assert config.get("log_file") == "env.log"

    @mock.patch.dict(
        os.environ,
        {
            "SPOTIFY_SCRAPER_CACHE_ENABLED": "invalid_bool",
            "SPOTIFY_SCRAPER_RETRIES": "not_a_number",
            "SPOTIFY_SCRAPER_TIMEOUT": "also_not_a_number",
            "SPOTIFY_SCRAPER_RATE_LIMIT_REQUESTS": "invalid_int",
        },
    )
    def test_from_env_invalid_values(self):
        """Test loading config from environment with invalid values."""
        config = Config(use_env=True)

        # Boolean values: invalid_bool doesn't match valid values, so it's set to False
        assert config.get("cache_enabled") is False  # Set to False for invalid boolean

        # Integer values: should use defaults for invalid integers
        assert config.get("retries") == 3  # Default
        assert config.get("timeout") == 30  # Default
        assert config.get("rate_limit_requests") == 10  # Default

    def test_repr(self):
        """Test string representation of config."""
        config = Config()

        repr_str = repr(config)
        assert "Config" in repr_str
        assert "values" in repr_str

    def test_update_from_dict_unknown_keys(self):
        """Test updating config with unknown keys."""
        config = Config()

        # Unknown keys should be ignored with warning
        config_dict = {"timeout": 60, "unknown_key": "value"}

        # This should not raise an exception
        config._update_from_dict(config_dict)

        assert config.get("timeout") == 60
        assert config.get("unknown_key") is None

    def test_config_with_file_and_dict(self):
        """Test config with both file and dict (dict should override file)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"timeout": 60, "retries": 5}, f)
            temp_file = f.name

        try:
            config = Config(
                config_file=temp_file,
                config_dict={"timeout": 90},  # This should override file value
            )

            assert config.get("timeout") == 90  # From dict
            assert config.get("retries") == 5  # From file
        finally:
            os.unlink(temp_file)
