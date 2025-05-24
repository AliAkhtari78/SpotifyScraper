"""Tests for auth.session module."""

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from spotify_scraper.auth.session import Session
from spotify_scraper.core.exceptions import AuthenticationError


class TestSession:
    """Test Session class."""

    def test_init_default(self):
        """Test default session initialization."""
        session = Session()
        
        assert session.cookies == {}
        assert session.headers == {}
        assert session.auth_token is None
        assert not session.is_authenticated()

    def test_init_with_data(self):
        """Test session initialization with data."""
        cookies = {"session_id": "12345"}
        headers = {"User-Agent": "TestAgent/1.0"}
        auth_token = "Bearer token123"
        
        session = Session(
            cookies=cookies,
            headers=headers,
            auth_token=auth_token
        )
        
        assert session.cookies == cookies
        assert session.headers == headers
        assert session.auth_token == auth_token
        assert session.is_authenticated()

    def test_is_authenticated_with_cookies(self):
        """Test authentication check with cookies."""
        session = Session(cookies={"sp_dc": "test_cookie"})
        assert session.is_authenticated()
        
        session = Session(cookies={"other": "cookie"})
        assert not session.is_authenticated()

    def test_is_authenticated_with_token(self):
        """Test authentication check with auth token."""
        session = Session(auth_token="Bearer token123")
        assert session.is_authenticated()
        
        session = Session(auth_token=None)
        assert not session.is_authenticated()

    def test_from_cookies_file_success(self):
        """Test loading session from cookies file."""
        cookie_content = """# Netscape HTTP Cookie File
# This is a generated file!  Do not edit.

.spotify.com	TRUE	/	TRUE	1234567890	sp_dc	test_dc_value
.spotify.com	TRUE	/	FALSE	1234567890	sp_key	test_key_value
.spotify.com	TRUE	/	TRUE	1234567890	sp_t	test_t_value
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(cookie_content)
            temp_file = f.name
        
        try:
            session = Session.from_cookies_file(temp_file)
            
            assert "sp_dc" in session.cookies
            assert session.cookies["sp_dc"] == "test_dc_value"
            assert "sp_key" in session.cookies
            assert session.cookies["sp_key"] == "test_key_value"
            assert "sp_t" in session.cookies
            assert session.cookies["sp_t"] == "test_t_value"
            assert session.is_authenticated()
        finally:
            Path(temp_file).unlink()

    def test_from_cookies_file_not_found(self):
        """Test loading session from non-existent file."""
        with pytest.raises(FileNotFoundError):
            Session.from_cookies_file("non_existent_cookies.txt")

    def test_from_cookies_file_empty(self):
        """Test loading session from empty cookies file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            session = Session.from_cookies_file(temp_file)
            assert session.cookies == {}
            assert not session.is_authenticated()
        finally:
            Path(temp_file).unlink()

    def test_from_cookies_file_malformed(self):
        """Test loading session from malformed cookies file."""
        cookie_content = """# Malformed cookie file
not enough fields
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(cookie_content)
            temp_file = f.name
        
        try:
            session = Session.from_cookies_file(temp_file)
            assert session.cookies == {}
        finally:
            Path(temp_file).unlink()

    def test_save_and_load(self):
        """Test saving and loading session."""
        original_session = Session(
            cookies={"sp_dc": "test_dc", "sp_key": "test_key"},
            headers={"User-Agent": "TestAgent/1.0"},
            auth_token="Bearer token123"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save session
            original_session.save(temp_file)
            
            # Load session
            loaded_session = Session.load(temp_file)
            
            assert loaded_session.cookies == original_session.cookies
            assert loaded_session.headers == original_session.headers
            assert loaded_session.auth_token == original_session.auth_token
            assert loaded_session.is_authenticated()
        finally:
            Path(temp_file).unlink()

    def test_load_non_existent(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            Session.load("non_existent_session.json")

    def test_load_invalid_json(self):
        """Test loading from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                Session.load(temp_file)
        finally:
            Path(temp_file).unlink()

    def test_save_creates_directory(self):
        """Test save creates parent directory if needed."""
        session = Session(cookies={"test": "cookie"})
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "session.json"
            
            session.save(str(file_path))
            
            assert file_path.exists()
            assert file_path.parent.exists()

    def test_update_cookies(self):
        """Test updating cookies."""
        session = Session(cookies={"old": "cookie"})
        
        session.update_cookies({"new": "cookie", "another": "one"})
        
        assert session.cookies == {
            "old": "cookie",
            "new": "cookie",
            "another": "one"
        }

    def test_update_headers(self):
        """Test updating headers."""
        session = Session(headers={"User-Agent": "OldAgent/1.0"})
        
        session.update_headers({
            "User-Agent": "NewAgent/2.0",
            "Accept": "application/json"
        })
        
        assert session.headers == {
            "User-Agent": "NewAgent/2.0",
            "Accept": "application/json"
        }

    def test_clear(self):
        """Test clearing session data."""
        session = Session(
            cookies={"sp_dc": "test"},
            headers={"User-Agent": "Test"},
            auth_token="Bearer token"
        )
        
        assert session.is_authenticated()
        
        session.clear()
        
        assert session.cookies == {}
        assert session.headers == {}
        assert session.auth_token is None
        assert not session.is_authenticated()

    def test_validate_success(self):
        """Test successful session validation."""
        session = Session(cookies={"sp_dc": "valid_cookie"})
        
        # Should not raise
        session.validate()

    def test_validate_failure(self):
        """Test session validation failure."""
        session = Session()  # No authentication
        
        with pytest.raises(AuthenticationError) as exc_info:
            session.validate()
        
        assert "Session is not authenticated" in str(exc_info.value)

    def test_to_dict(self):
        """Test converting session to dictionary."""
        session = Session(
            cookies={"sp_dc": "test"},
            headers={"User-Agent": "Test"},
            auth_token="Bearer token"
        )
        
        data = session.to_dict()
        
        assert data == {
            "cookies": {"sp_dc": "test"},
            "headers": {"User-Agent": "Test"},
            "auth_token": "Bearer token"
        }

    def test_from_dict(self):
        """Test creating session from dictionary."""
        data = {
            "cookies": {"sp_dc": "test"},
            "headers": {"User-Agent": "Test"},
            "auth_token": "Bearer token"
        }
        
        session = Session.from_dict(data)
        
        assert session.cookies == data["cookies"]
        assert session.headers == data["headers"]
        assert session.auth_token == data["auth_token"]

    def test_from_dict_partial(self):
        """Test creating session from partial dictionary."""
        data = {"cookies": {"sp_dc": "test"}}
        
        session = Session.from_dict(data)
        
        assert session.cookies == data["cookies"]
        assert session.headers == {}
        assert session.auth_token is None

    def test_get_auth_headers_with_token(self):
        """Test getting auth headers with token."""
        session = Session(auth_token="Bearer token123")
        
        headers = session.get_auth_headers()
        
        assert headers == {"Authorization": "Bearer token123"}

    def test_get_auth_headers_without_token(self):
        """Test getting auth headers without token."""
        session = Session()
        
        headers = session.get_auth_headers()
        
        assert headers == {}

    def test_repr(self):
        """Test string representation."""
        session = Session(cookies={"sp_dc": "test"})
        
        repr_str = repr(session)
        
        assert "Session" in repr_str
        assert "authenticated=True" in repr_str

    @mock.patch('spotify_scraper.auth.session.requests.get')
    def test_from_browser_extension(self, mock_get):
        """Test loading session from browser extension export."""
        # This would test browser extension integration if implemented
        pass

    def test_cookie_expiry_handling(self):
        """Test handling of expired cookies."""
        # This would test cookie expiry if implemented
        pass