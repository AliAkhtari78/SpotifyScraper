"""Package-level sanity checks."""

import re

import spotify_scraper


def test_version_is_pep440() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:\.dev\d+|rc\d+)?", spotify_scraper.__version__)
