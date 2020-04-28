# -*- coding: utf-8 -*-

# Copyright 2020 Ali Akhtari <https://github.com/AliAkhtari78>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from requests.sessions import Session
from bs4 import BeautifulSoup
from .request import Request
import yaml
import eyed3
import os


class Scraper:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _str_to_json(string: str) -> dict:
        json_acceptable_string = string.replace('\n', '').strip()
        converted_string = yaml.load(json_acceptable_string, Loader=yaml.FullLoader)

        return converted_string

    @staticmethod
    def _ms_to_readable(millis: int) -> str:
        seconds = int(millis / 1000) % 60
        minutes = int(millis / (1000 * 60)) % 60
        hours = int(millis / (1000 * 60 * 60)) % 24
        if hours == 0:
            return "%d:%d" % (minutes, seconds)
        else:
            return "%d:%d:%d" % (hours, minutes, seconds)

    @staticmethod
    def _turn_url_to_embed(url: str) -> str:
        if 'embed' in url:
            return url
        else:
            return url.replace('/track/', '/embed/track/')

    def _image_downloader(self, url: str, file_name: str, path: str = '') -> str:
        request = self.session.get(url=url, stream=True)
        ext = request.headers['content-type'].split('/')[
            -1]  # converts response headers mime type to an extension (may not work with everything)
        if path == '':
            pass
        else:
            path = path + '//'
        file_name = "".join(x for x in file_name if x.isalnum())
        saving_directory = path + file_name + '.' + ext
        with open(saving_directory,
                  'wb') as f:  # open the file to write as binary - replace 'wb' with 'w' for text files
            for chunk in request.iter_content(1024):  # iterate on stream using 1KB packets
                f.write(chunk)  # write the file
        return saving_directory

    def _preview_mp3_downloader(self, url: str, file_name: str, path: str = '', with_cover: bool = False,
                                cover_url: str = '') -> str:
        if path == '':
            pass
        else:
            path = path + '//'

        file_name = file_name = "".join(x for x in file_name if x.isalnum())
        saving_directory = path + file_name + '.mp3'
        song = self.session.get(url=url, stream=True)
        with open(saving_directory, 'wb') as f:
            f.write(song.content)

        if with_cover:
            audio_file = eyed3.load(saving_directory)
            if audio_file.tag is None:
                audio_file.initTag()

            image_path = self._image_downloader(url=cover_url, file_name=file_name, path=path)
            audio_file.tag.images.set(3, open(image_path, 'rb').read(), 'image/')
            audio_file.tag.save()
            os.remove(path=image_path)

        return saving_directory

    def get_track_url_info(self, url: str) -> dict:
        try:
            page_content = self.session.get(url=self._turn_url_to_embed(url=url), stream=True).content
            try:
                bs_instance = BeautifulSoup(page_content, "lxml")
                url_information = self._str_to_json(string=bs_instance.find("script", {"id": "resource"}).contents[0])
                title = url_information['name']
                preview_mp3 = url_information['preview_url']
                duration = self._ms_to_readable(millis=int(url_information['duration_ms']))
                artist_name = url_information['artists'][0]['name']
                artist_url = url_information['artists'][0]['external_urls']['spotify']
                album_title = url_information['album']['name']
                album_cover_url = url_information['album']['images'][0]['url']
                album_cover_height = url_information['album']['images'][0]['height']
                album_cover_width = url_information['album']['images'][0]['width']
                release_date = url_information['album']['release_date']
                total_tracks = url_information['album']['total_tracks']
                type_ = url_information['album']['type']

                return {
                    'title': title,
                    'preview_mp3': preview_mp3,
                    'duration': duration,
                    'artist_name': artist_name,
                    'artist_url': artist_url,
                    'album_title': album_title,
                    'album_cover_url': album_cover_url,
                    'album_cover_height': album_cover_height,
                    'album_cover_width': album_cover_width,
                    'release_date': release_date,
                    'total_tracks': total_tracks,
                    'type_': type_,
                    'ERROR': None,
                }
            except:
                try:
                    bs_instance = BeautifulSoup(page_content, "lxml")
                    error = bs_instance.find('div', {'class': 'content'}).text
                    if "Sorry, couldn't find that." in error:
                        return {"ERROR": "The provided url doesn't belong to any song on Spotify."}
                except:
                    return {"ERROR": "The provided url is malformed."}
        except:
            raise

    def download_cover(self, url: str, path: str = '') -> str:
        try:
            if 'playlist' in url:
                page_content = self.session.get(url=url, stream=True).content
                try:
                    bs_instance = BeautifulSoup(page_content, "lxml")
                    album_title = bs_instance.find('title').text
                    cover_url = bs_instance.find('meta', property='og:image')['content']
                    try:
                        return self._image_downloader(url=cover_url, file_name=album_title,
                                                      path=path)
                    except:
                        return "Couldn't download the cover."

                except:
                    return "The provided url doesn't belong to any song on Spotify."



            else:
                page_content = self.session.get(url=self._turn_url_to_embed(url=url), stream=True).content
                try:
                    bs_instance = BeautifulSoup(page_content, "lxml")
                    url_information = self._str_to_json(
                        string=bs_instance.find("script", {"id": "resource"}).contents[0])
                    title = url_information['name']
                    album_title = url_information['album']['name']
                    album_cover_url = url_information['album']['images'][0]['url']

                    try:
                        return self._image_downloader(url=album_cover_url, file_name=title + '-' + album_title,
                                                      path=path)

                    except:
                        return "Couldn't download the cover."
                except:
                    try:
                        bs_instance = BeautifulSoup(page_content, "lxml")
                        error = bs_instance.find('div', {'class': 'content'}).text
                        if "Sorry, couldn't find that." in error:
                            return "The provided url doesn't belong to any song on Spotify."
                    except:
                        raise
        except:
            raise

    def download_preview_mp3(self, url: str, path: str = '', with_cover: bool = False) -> str:
        try:
            page_content = self.session.get(url=self._turn_url_to_embed(url=url), stream=True).content
            try:
                bs_instance = BeautifulSoup(page_content, "lxml")
                url_information = self._str_to_json(string=bs_instance.find("script", {"id": "resource"}).contents[0])
                title = url_information['name']
                album_title = url_information['album']['name']
                preview_mp3 = url_information['preview_url']
                album_cover_url = url_information['album']['images'][0]['url']

                try:
                    return self._preview_mp3_downloader(url=preview_mp3, file_name=title + '-' + album_title, path=path,
                                                        with_cover=with_cover, cover_url=album_cover_url)

                except:
                    return "Couldn't download the cover."
            except:
                try:
                    bs_instance = BeautifulSoup(page_content, "lxml")
                    error = bs_instance.find('div', {'class': 'content'}).text
                    if "Sorry, couldn't find that." in error:
                        return "The provided url doesn't belong to any song on Spotify."
                except:
                    raise
        except:
            raise

    def get_playlist_url_info(self, url: str) -> dict:
        try:
            if '?si' in url:
                url = url.split('?si')[0]
            page = self.session.get(url=url, stream=True).content
            try:
                bs_instance = BeautifulSoup(page, "lxml")
                tracks = bs_instance.find('ol', {'class': 'tracklist'})
                playlist_description = bs_instance.find('meta', {"name": "description"})['content']
                author_url = bs_instance.find('meta', property='music:creator')['content']
                author = author_url.split('/')[4]
                tracks_list = []
                album_title = bs_instance.find('title').text
                cover_url = bs_instance.find('meta', property='og:image')['content']
                temp_list = []
                counter = 0
                duration_list = tracks.find_all('span', {'class': 'total-duration'})
                for item in tracks.find_all('span', {"dir": "auto"}):
                    temp_list.append(item)
                    if len(temp_list) == 3:
                        try:
                            temp = {'track_name': temp_list[0].text, 'track_singer': temp_list[1].text,
                                    'track_album': temp_list[2].text,
                                    'duration': duration_list[counter].text}
                        except:
                            temp = {'track_name': temp_list[0].text, 'track_singer': temp_list[1].text,
                                    'track_album': temp_list[2].text,
                                    'duration': None}
                        tracks_list.append(temp)
                        temp_list = []
                        counter += 1

                data = {'album_title': album_title, 'cover_url': cover_url, 'author': author, 'author_url': author_url,
                        'playlist_description': playlist_description,
                        'tracks_list': tracks_list}
                return data
            except:
                return {"ERROR": "The provided url is malformed."}
        except:
            raise
