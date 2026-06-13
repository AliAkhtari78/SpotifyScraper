# SpotifyScraper Wiki

**Documentation has moved to ReadTheDocs:** https://spotifyscraper.readthedocs.io/

This wiki is no longer maintained. Please use the ReadTheDocs site above for
installation, guides, and the full API reference.

## 30-second quickstart

```bash
pip install spotifyscraper
```

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    print(track.name, "-", ", ".join(a.name for a in track.artists))
    print(track.to_dict())
```

## Links

- [Documentation (ReadTheDocs)](https://spotifyscraper.readthedocs.io/)
- [Installation](https://spotifyscraper.readthedocs.io/en/latest/getting-started/installation/)
- [Quickstart](https://spotifyscraper.readthedocs.io/en/latest/getting-started/quickstart/)
- [GitHub repository](https://github.com/AliAkhtari78/SpotifyScraper)
- [PyPI](https://pypi.org/project/spotifyscraper/)
