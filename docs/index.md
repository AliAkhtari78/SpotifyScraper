  
# Spotify Scraper  Documentation 
  
  
##  Overview  
Python **Spotify Web Player Scraper**, a fast high-level Spotify Web Player Scraper, to scrape and extract data from Spotify Web Player with the most efficient and fastest methods.  
instead of using Selenium, I used [requests](https://github.com/psf/requests) library to increase the speed of scraping.  
You can set cookies, headers, and proxy and download the cover and preview mp3 song of Spotify songs besides extracting the data from Spotify Web Player.	
  
# Getting Started with Spotify Scraper
Spotify Scraper is a fast and powerful Spotify scraper with Beautifulsoup and requests using Python.
- Extract title, preview mp3 URL, duration, artist name, artist URL, album title, album cover URL, album cover height, album cover width, release date, and total tracks from Spotify track URLs.
- Extract album title, cover URL, author, author URL, playlist description and tracks list of Spotify playlist URLs.
- Download preview MP3 file of Spotify track URLs and save it on your disk, you can even set cover of the track to MP3 file.
- Download the image file of Spotify track URLs.
- Set Cookies, Headers, and Proxy before extracting the data.

## Requirements  
- Python 3.6 +  
- Works on Linux, Windows, macOS, BSD  
- Internet connection  
  
## Quickstart
Assuming you have Python3.6 version above already:
 ``
$ pip install spotifyscraper
``
 you can also download the package from [github page](https://github.com/AliAkhtari78/SpotifyScraper) then install it:
-  ``$ git clone https://github.com/AliAkhtari78/SpotifyScraper.git``
- ``$sudo python3 setup.py install``

### Enjoy Using Spotify Scraper
``from SpotifyScraper.scraper import Scraper, Request``
``request = Request().request()``
``track_information = Scraper(session=request).get_track_url_info(url)``

* Replace url with Spotify track URL.
>If the given URL is valid, it will return a dict with the below keys:
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



## Install Guide
Spotify Scraper only works on =< Python 3.6  which you can get from:
* [Download Python](https://www.python.org/downloads/)
* Spotify Scraper use [requests](https://pypi.org/project/requests/) and [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) as main packages to extract data from Spotify web player.
* You can see [requirements.txt](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/requirements.txt) in this library Github page.
### Install Spotify Scraper
The easiest and fastest way to install Spotify Scraper is getting it's latest stable version from PyPI and install it using pip:
-  ``$ pip install -U spotifyscraper``

Or you can download Spotify Scraper and install it from GitHub:
- ``$ git clone https://github.com/AliAkhtari78/SpotifyScraper.git``
- ``$python setup.py install``

#### Note that it's better to install Spotify Scraper from PyPI rather download and install it from git.

 ## Verifying 
 To verify that Spotify Scraper is correctly installed, open a Python shell and import it. If no error shows up you are good to go.
<br>``>>> import SpotifyScraper`` 
<br>``>>> SpotifyScraper.__version__``
``1.0.5``

## Import Request
Spotify Scraper uses [requests](https://pypi.org/project/requests/) to retrieve and extract data from Spotify.
Before extracting data, you have to import and create requests session:
<br>``from SpotifyScraper.scraper import Request``<br>
after importing, you can create an instance of Request with the following line of code:
<br>``request = Request()``<br>
By default Request doesn't take any args, but you can pass and set the following parameters:
### cookie file
You can pass a **.txt** file as a cookie file to **Request()**.
To extract cookie file from your Chrome Browser you can use below  Chrome Extention to get **cookie_file.txt** :
[# cookies.txt](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg?hl=en)
after getting **cookies.txt**, you can pass the path of text file to the **Request()**:
<br>``Request(cookie_file='cookies.txt')``<br>


### Set header
beside passing cookie file to the Request, you can Also pass header to use it as request header when request try to extract data from Spotify.
note that header must be a dict like this:
<br>``{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',  
  'Accept': '*/*',  
  'DNT': '1',  
  'app-platform': 'WebPlayer',}``<br>
  and pass it to **Request()** like this:
<br>  ``Request(headers=headers)``<br>
### Set proxy:
Also proxy can be set to the **Request()** moduale, all you have to do is just passing a dict which include proxy data:
<br>``http_proxy = "http://127.0.0.1:80"``
``https_proxy = "https://127.0.0.1:443"``
``ftp_proxy = "ftp://127.0.0.1:21"``
``proxyDict = {"http": http_proxy,"https": https_proxy,"ftp": ftp_proxy}``
``Request(proxy=proxyDict)``<br>


## Import Scraper
Scraper module includes all the functions to scrape data from Spotify.
After importing and creating Request(), you should import Scraper with the following line of code:
<br>``from SpotifyScraper.scraper import Scraper``<br>
Then pass the request instance of Request() to Scraper:
<br>``scraper = Request().request()``<br>
After this, you can use all the available methods from Scraper module.


### Extract Spotify Track Informations
To extract spotify track data, you should call get_track_url_info method.
follow the example code below to scrape the data:
<br>``from SpotifyScraper.scraper import Scraper, Request``<br>
``request = Request().request()``<br>
``scraper = Scraper(session=request)``<br>
``track_information = scraper.get_track_url_info(url=url)``<br>
Just replace the url with spotify track URL.
If the given URL is valid, it will return a dict which you can have access with below keys:
- title
- preview_mp3
- duration
- artist_name
- artist_url
- album_title
- album_cover_url
- album_cover_height
- album_cover_width
- release_date
- total_tracks
- type_
 - ERROR
In case of invalid URL or other issues, the value of ``ERROR`` will be the explanation of the issue, otherwise it will be **None**.




### Extract Spotify Playlist Informations
To extract spotify playlist data, you should call get_playlist_url_infomethod.
follow the example code below to scrape the data:
<br>``from SpotifyScraper.scraper import Scraper, Request``<br>
``request = Request().request()``<br>
``scraper = Scraper(session=request)``<br>
``playlist_information = scraper.get_playlist_url_info(url=url)``<br>
Just replace the url with spotify playlist URL.
If the given URL is valid, it will return a dict which you can have access with below keys:
- album_title
- cover_url
- author
- author_url
- playlist_description
- tracks_list
- ERROR

In case of invalid URL or other issues, the value of ``ERROR`` will be the explanation of the issue, otherwise it will be **None**.
**tracks_list** is a list of tracks in which every track is stored in a dict includes the data of every track. tracks_list has the following information inside it:
- track_name
- track_singer
- track_album
- duration



### Download Cover Art of Spotify Tracks
**get_track_url_info()** is a method inside Scraper that allows you to download the cover of every Spotify track you want.
By default  **get_track_url_info()** download the cover inside the root directory, but you can pass a path as a string to set download path.
the name of the cover will be the same as the track song's name.
if the provided track URL is valid, it will return the path of downloaded cover as string.
You can use the example code below to download the cover of Spotify track URLs:
<br>``from SpotifyScraper.scraper import Scraper, Request``<br>
``request = Request().request()``<br>
``scraper = Scraper(session=request)``<br>
``cover_downloaded_path = scraper.download_cover(url=url,path=path)``<br>
Just replace the URL with Spotify Track URL and replace the path with the path you want to download to, you can also remove **path=path** to download covers at the root directory.



### Download Preview mp3 of Spotify Tracks
Every song on Spotify has a preview song which is a short mp3 file **usually between 20 to 40 seconds** that is considered as a demo of every song.
You can download this preview mp3 files only by calling the **download_preview_mp3()** method.
Same as **get_track_url_info()**,  **download_preview_mp3()** download the mp3 inside the root directory, but you can pass a path as a string to set download path.
besides downloading the mp3, you can set **with_cover=True** to download and combine the cover of the song with the mp3 file.
if the provided track URL is valid, it will return the path of downloaded mp3 as string.
the name of the mp3 file will be the same as the track song's name.
You can use the example code below to download the preview mp3 of Spotify track URLs song:
<br>``from SpotifyScraper.scraper import Scraper, Request``<br>
``request = Request().request()``<br>
``scraper = Scraper(session=request)``<br>
``mp3_downloaded_path = scraper.download_preview_mp3(url=url, path=path, with_cover=True)``<br>
Just replace the URL with Spotify Track URL and replace the path with the path you want to download to, you can remove **path=path** to download covers at the root directory, also you can remove **with_cover=True** to only download the mp3 without cover of the song.

## Save the log file to disk
If something went wring, in order to find the problem and report the bug to me, you can set log to True to save the log file in your disk:
``Scraper(session=request, log=True)``

## Why Spotify Scraper
To extract data from Spotify, there is two way to do that:
You can go to the Spotify API page and sign up as a developer and get the ... 
Or you can just use **Spotify Scraper** to extract data from Spotify in a fast and super easy way,
also even with Spotify API you won't be able to download mp3 and cover of the songs.


## Bugs report, Need Enhancement?
This library is a free open source project, which you can use it for free and report any bug or if you need to add a new feature you can always send me an email or report it in Spotify Scraper Github Page:
[https://github.com/AliAkhtari78/SpotifyScraper/issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
or get in touch with me by my website:
[ali akhtari](https://aliakhtari.com/)

## License
Copyright (c) 2020 Ali Akhtari  
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  
  
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.