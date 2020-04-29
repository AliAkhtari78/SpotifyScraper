
# Spotify Scraper


##  Overview
Python **Spotify Web Player Scraper**, a fast high-level Spotify Web Player Scraper, to scrape and extract data from Spotify Web Player with the most efficient and fastest methods.
instead of using Selenium, I used [requests](https://github.com/psf/requests) library to increase the speed of scraping.
You can set cookies, headers and proxy and download the cover and preview mp3 song of Spotify songs beside the scraping.

## Requirements
- Python 3.6 +
- Works on Linux, Windows, macOS, BSD
- Internet connection

## Installing
You can install this package as simple as type a command in your CMD or Terminal.
The quick way:
```sh
$ pip install spotifyscraper
```
or
do it in the hard way:

``
$ git clone https://github.com/AliAkhtari78/SpotifyScraper.git 
``
 ``
$sudo python3 setup.py install
``
## Documentation

Check out [Read The Docs](https://spotifyscraper.readthedocs.io/en/latest/) for a more in-depth explanation, with examples, troubleshooting issues, and more useful information.
## Extract Spotify track information by URL
- ``
from SpotifyScraper.scraper import Scraper, Request
``
> Import SpotifyScraper to use it
- ``
 request = Request().request()
``
> Create requests using Request which was imported before,
> You can also pass cookie_file, header	and proxy inside Request().
> Default is None.
- ``
print(Scraper(session=request).get_track_url_info(url='https://open.spotify.com/track/7wqpAYuSk84f0JeqCIETRV?si=b35Rzak1RgWvBAnbJteHkA'))
``
> Call get_track_url_info function from Scraper to extract all the infromation from url.
> If the given URL is valid, it will return a dict with the below keys:
> - title
> - preview_mp3
> - duration
> - artist_name
> - artist_url
> - album_title
> - album_cover_url
> - album_cover_height
> - album_cover_width
> - release_date
> - total_tracks
> - type_
> - ERROR

- ``
$ {
'title': 'The Future Never Dies',
 'preview_mp3': 'https://p.scdn.co/mp3-preview/2d706ceae19cfbc778988df6ad5c60828dbd8389?cid=a46f5c5745a14fbf826186da8da5ecc3',
  'duration': '4:3',
   'artist_name': 'Scorpions',
 'artist_url':'https://open.spotify.com/artist/27T030eWyCQRmDyuvr1kxY',
  'album_title': 'Humanity Hour 1', 
 'album_cover_url':'https://i.scdn.co/image/ab67616d0000b273e14019d431204ff27785e349', 
 'album_cover_height': 640, 
 'album_cover_width': 640, 
 'release_date': '2007-01-01', 
 'total_tracks': 12,
  'type_': 'album', 
  'ERROR': None}
``

## Extract Spotify playlist information by URL
- ``
from SpotifyScraper.scraper import Scraper, Request
``

- ``
 request = Request().request() ``
 
-  ``playlist_info = Scraper(session=request).get_playlist_url_info(url='https://open.spotify.com/playlist/37i9dQZF1DX74DnfGTwugU')
 ``
> Call get_playlist_url_info function from Scraper to extract all the infromation from url.
> If the given URL is valid, it will return a dict with the below keys:
> - album_title
> - cover_url
> - author
> - author_url
> - playlist_description
> - tracks_list
> - ERROR
 
## Download Spotify song cover by URL
- ``
from SpotifyScraper.scraper import Scraper, Request
``

- ``
 request = Request().request() ``
 
-  ``path = Scraper(session=request).download_cover(url='https://open.spotify.com/track/7wqpAYuSk84f0JeqCIETRV?si=b35Rzak1RgWvBAnbJteHkA')
 ``
 > Call download_cover function from Scraper to download the cover of the provided song.
 
 **if the provided URL is valid, it will return the path of downloaded  cover to you.**


## Download Spotify preview song by URL
- ``
from SpotifyScraper.scraper import Scraper, Request
``

- ``
 request = Request().request() ``
 
-  ``path = Scraper(session=request).download_preview_mp3(url='https://open.spotify.com/track/7wqpAYuSk84f0JeqCIETRV?si=b35Rzak1RgWvBAnbJteHkA')
 ``
  > Call download_preview_mp3 function from Scraper to download the preview mp3 song of the provided URL.
 
 **if the provided URL is valid, it will return the path of downloaded mp3 to you.**

 ## Get in touch

-   Report bugs, suggest features, or view the source code  [on GitHub](https://github.com/AliAkhtari78/SpotifyScraper).
- [Read the doc](https://spotifyscraper.readthedocs.io/en/latest/?) to use all provided functions of this library.
- get in touch with me by my website:
[ali akhtari](https://aliakhtari.com/)