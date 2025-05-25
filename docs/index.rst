.. SpotifyScraper documentation master file

SpotifyScraper Documentation
============================

The Ultimate Python Library for Spotify Data Extraction

.. image:: https://badge.fury.io/py/spotifyscraper.svg
   :target: https://badge.fury.io/py/spotifyscraper
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/spotifyscraper.svg
   :target: https://pypi.org/project/spotifyscraper/
   :alt: Python Support

.. image:: https://readthedocs.org/projects/spotifyscraper/badge/?version=latest
   :target: https://spotifyscraper.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Welcome to SpotifyScraper
-------------------------

SpotifyScraper is a powerful, modern Python library designed to extract data from Spotify's web player without requiring API credentials. Built for reliability, performance, and ease of use, it provides a comprehensive toolkit for accessing Spotify's vast music database.

🚀 Why SpotifyScraper?
~~~~~~~~~~~~~~~~~~~~~~

- **Zero Authentication**: No API keys, no OAuth, no hassle
- **Comprehensive Data**: Extract tracks, albums, artists, playlists, and lyrics
- **High Performance**: Optimized for speed with intelligent caching
- **Type Safe**: Full type hints for better IDE support
- **Battle Tested**: Used in production by thousands of developers

Quick Start
-----------

Installation::

    pip install spotifyscraper

Basic Usage::

    from spotify_scraper import SpotifyClient

    # Initialize the client
    client = SpotifyClient()

    # Get track information
    track = client.get_track_info("https://open.spotify.com/track/...")
    print(f"Track: {track['name']} by {track['artist']}")

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/installation
   guide/index
   guide/basic-usage

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   examples/index
   examples/quickstart
   examples/cli
   examples/advanced

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/client
   api/extractors
   api/exceptions
   api/media
   api/utils

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   advanced/architecture
   advanced/custom-extractors
   advanced/performance
   advanced/scaling

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   features
   faq
   troubleshooting
   migration
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`