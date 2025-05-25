"""Tests for auth.session module."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from spotify_scraper.auth.session import Request, Session


class TestSession:
    """Test Session class."""

    def test_init_default(self):
        """Test default session initialization."""
        session = Session()

        assert session.access_token is None
        assert session.cookies == {}
        assert session.headers == {}
        assert session.expires_at is None
        assert session.is_anonymous is True

    def test_init_with_data(self):
        """Test session initialization with data."""
        access_token = "test_token_123"
        cookies = {"session_id": "12345"}
        headers = {"User-Agent": "TestAgent/1.0"}

        session = Session(access_token=access_token, cookies=cookies, headers=headers)

        assert session.access_token == access_token
        assert session.cookies == cookies
        assert session.headers == headers
        assert session.is_anonymous is False

    def test_is_valid_with_token(self):
        """Test session validity with access token."""
        session = Session(access_token="valid_token")
        assert session.is_valid() is True

        session = Session()
        assert session.is_valid() is False

    def test_is_valid_with_cookies(self):
        """Test session validity with cookies."""
        session = Session(cookies={"sp_dc": "test_cookie"})
        assert session.is_valid() is True

    def test_is_valid_expired(self):
        """Test session validity when expired."""
        session = Session(access_token="token")
        session.expires_at = datetime.now() - timedelta(hours=1)
        assert session.is_valid() is False

    def test_set_access_token(self):
        """Test setting access token."""
        session = Session()
        assert session.is_anonymous is True

        session.set_access_token("new_token", expires_in=3600)

        assert session.access_token == "new_token"
        assert session.is_anonymous is False
        assert session.expires_at is not None
        assert session.expires_at > datetime.now()

    def test_add_cookies(self):
        """Test adding cookies."""
        session = Session()

        session.add_cookies({"sp_dc": "cookie1", "sp_key": "cookie2"})

        assert session.cookies == {"sp_dc": "cookie1", "sp_key": "cookie2"}

        # Add more cookies
        session.add_cookies({"sp_t": "cookie3"})
        assert len(session.cookies) == 3

    def test_get_auth_headers(self):
        """Test getting auth headers."""
        session = Session(access_token="test_token", headers={"User-Agent": "Test"})

        headers = session.get_auth_headers()

        assert headers["Authorization"] == "Bearer test_token"
        assert headers["User-Agent"] == "Test"

    def test_get_auth_headers_no_token(self):
        """Test getting auth headers without token."""
        session = Session(headers={"User-Agent": "Test"})

        headers = session.get_auth_headers()

        assert "Authorization" not in headers
        assert headers["User-Agent"] == "Test"

    def test_save_and_load(self):
        """Test saving and loading session."""
        original_session = Session(
            access_token="test_token",
            cookies={"sp_dc": "test_dc"},
            headers={"User-Agent": "TestAgent/1.0"},
        )
        original_session.set_access_token("test_token", expires_in=3600)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            # Save session
            assert original_session.save_to_file(temp_file) is True

            # Load session
            loaded_session = Session.load_from_file(temp_file)

            assert loaded_session is not None
            assert loaded_session.access_token == original_session.access_token
            assert loaded_session.cookies == original_session.cookies
            assert loaded_session.headers == original_session.headers
            assert loaded_session.is_anonymous == original_session.is_anonymous
        finally:
            Path(temp_file).unlink()

    def test_load_non_existent(self):
        """Test loading from non-existent file."""
        session = Session.load_from_file("non_existent_session.json")
        assert session is None

    def test_save_failure(self):
        """Test save failure handling."""
        session = Session()

        # Try to save to invalid path
        result = session.save_to_file("/invalid/path/session.json")
        assert result is False

    def test_clear(self):
        """Test clearing session data."""
        session = Session(
            access_token="test_token", cookies={"sp_dc": "test"}, headers={"User-Agent": "Test"}
        )
        session.expires_at = datetime.now() + timedelta(hours=1)

        assert session.is_anonymous is False

        session.clear()

        assert session.access_token is None
        assert session.cookies == {}
        assert session.headers == {}
        assert session.expires_at is None
        assert session.is_anonymous is True

    def test_refresh(self):
        """Test refresh method (currently unimplemented)."""
        session = Session()
        result = session.refresh()
        assert result is False  # Should return False as it's not implemented


class TestRequest:
    """Test Request compatibility class."""

    def test_init(self):
        """Test Request initialization."""
        request = Request(
            cookie_file="cookies.txt",
            headers={"User-Agent": "Test"},
            proxy="http://proxy.example.com",
        )

        assert isinstance(request.session, Session)
        assert request.session.headers == {"User-Agent": "Test"}

    def test_request_method(self):
        """Test request method returns session."""
        request = Request()
        session = request.request()

        assert isinstance(session, Session)
