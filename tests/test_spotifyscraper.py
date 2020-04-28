import unittest

from SpotifyScraper.scraper import Scraper
from SpotifyScraper.request import Request


class TestSpotifyScraper(unittest.TestCase):
    if __name__ == "__main__":
        temp = Scraper(session=Request().request()).get_playlist_url_info(
            url='https://open.spotify.com/playlist/4aT59fj7KajejaEcjYtqPi?si=W9G4j4p7QhamrPdGjm4UXw')
