"""Test cases for NoneType handling in JSON parser (Issue #71)"""

import pytest

from spotify_scraper.core.exceptions import ParsingError
from spotify_scraper.parsers.json_parser import extract_track_data, get_nested_value


class TestNoneTypeHandling:
    """Test cases for proper handling of None values in track data"""

    def test_track_data_is_none(self):
        """Test when track_data is None"""
        json_data = {"props": {"pageProps": {"state": {"data": {"entity": None}}}}}

        with pytest.raises(ParsingError) as excinfo:
            extract_track_data(json_data)

        assert "No track data found" in str(excinfo.value)

    def test_track_data_is_not_dict(self):
        """Test when track_data is not a dictionary"""
        json_data = {"props": {"pageProps": {"state": {"data": {"entity": "not a dict"}}}}}

        with pytest.raises(ParsingError) as excinfo:
            extract_track_data(json_data)

        assert "is not a dictionary" in str(excinfo.value)

    def test_artists_field_is_none(self):
        """Test when artists field is None (Issue #71)"""
        track_data = {
            "id": "test123",
            "name": "Test Track",
            "uri": "spotify:track:test123",
            "artists": None,  # This was causing the NoneType error
        }

        # This should not raise an error
        json_data = {"props": {"pageProps": {"state": {"data": {"entity": track_data}}}}}
        result = extract_track_data(json_data)

        assert result["id"] == "test123"
        assert result["name"] == "Test Track"
        assert "artists" not in result or result.get("artists") == []

    def test_nested_none_values(self):
        """Test various nested None values that could cause issues"""
        track_data = {
            "id": "test123",
            "name": "Test Track",
            "uri": "spotify:track:test123",
            "artists": None,
            "album": None,
            "audioPreview": None,
            "contentRating": None,
            "visualIdentity": None,
            "lyrics": None,
        }

        json_data = {"props": {"pageProps": {"state": {"data": {"entity": track_data}}}}}

        # This should not raise an error
        result = extract_track_data(json_data)

        assert result["id"] == "test123"
        assert result["name"] == "Test Track"
        assert result["is_explicit"] is False  # Default value
        assert result["is_playable"] is True  # Default value

    def test_partial_none_values(self):
        """Test when some nested objects have None values"""
        track_data = {
            "id": "test123",
            "name": "Test Track",
            "uri": "spotify:track:test123",
            "artists": [{"name": "Test Artist", "uri": "spotify:artist:test", "profile": None}],
            "album": {"name": "Test Album", "coverArt": None},
        }

        json_data = {"props": {"pageProps": {"state": {"data": {"entity": track_data}}}}}

        # This should not raise an error
        result = extract_track_data(json_data)

        assert result["id"] == "test123"
        assert len(result.get("artists", [])) == 1
        assert result["artists"][0]["name"] == "Test Artist"
        assert result["album"]["name"] == "Test Album"

    def test_get_nested_value_with_none(self):
        """Test get_nested_value function with None values"""
        data = {"a": {"b": None}}

        # Should return None when path leads to None
        assert get_nested_value(data, "a.b") is None

        # Should return default when trying to go deeper than None
        assert get_nested_value(data, "a.b.c", default="default") == "default"

    def test_real_issue_71_scenario(self):
        """Test the specific scenario from issue #71"""
        # Simulate what might be happening with the Chinese track
        track_data = {
            "id": "0VqSdtXseb9khdZrnYVyM1",
            "name": "不為誰而作的歌",
            "uri": "spotify:track:0VqSdtXseb9khdZrnYVyM1",
            "artists": None,  # This could be the issue
            "album": {
                "name": "和自己對話 實驗專輯",
                "uri": "spotify:album:test",
            },
        }

        json_data = {"props": {"pageProps": {"state": {"data": {"entity": track_data}}}}}

        # This should not raise a TypeError
        result = extract_track_data(json_data)

        assert result["id"] == "0VqSdtXseb9khdZrnYVyM1"
        assert result["name"] == "不為誰而作的歌"
        assert "artists" not in result or result.get("artists") == []
