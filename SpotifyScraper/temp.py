# # # Importing the dependencies
# # # This is needed to create a lxml object that uses the css selector
# # from lxml.etree import fromstring
# #
# # # The requests library
# # import requests
# #
# # response = requests.post('https://open.spotify.com/embed/track/1TPICPxMn2eEJ0We2gwvNa?si=KSaiBtcNSdiE0aIL_g8s6g')
# #
# # # The data that we are looking is in the second
# # # Element of the response and has the key 'data',
# # # so that is what's returned
# # print(response)
# # import requests
# # import time
# #
# # request_session = requests.Session()
# #
# # r = requests.get("https://i.scdn.co/image/ab67616d0000b2738583df1a14bea9175f9ac520", stream=True)
# # ext = r.headers['content-type'].split('/')[
# #     -1]  # converts response headers mime type to an extension (may not work with everything)
# # with open("%s.%s" % (time.time(), ext),
# #           'wb') as f:  # open the file to write as binary - replace 'wb' with 'w' for text files
# #     for chunk in r.iter_content(1024):  # iterate on stream using 1KB packets
# #         f.write(chunk)  # write the file
# # url = 'https://p.scdn.co/mp3-preview/9ee9482b3236de15f31a95d0c9424d0cbd49964a?cid=a46f5c5745a14fbf826186da8da5ecc3'
# #
# # import requests
# #
# # doc = requests.get(url, stream=True)
# # with open('song.mp3', 'wb') as f:
# #     f.write(doc.content)
# import eyed3
#
# audiofile = eyed3.load("Don't Start Now-Don't Start Now.mp3")
# if (audiofile.tag == None):
#     audiofile.initTag()
#
# audiofile.tag.images.set(3, open("Don't Start Now-Don't Start Now.jpeg", 'rb').read(), 'image/')
# audiofile.tag.save()
import requests
from bs4 import BeautifulSoup

page = requests.get(url='https://open.spotify.com/playlist/5r0ucEuV65SDtcNYA4m4KF', stream=True, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'Accept': '*/*',
    'DNT': '1',
    'app-platform': 'WebPlayer',
}).content
bs_instance = BeautifulSoup(page, "lxml")
tracks = bs_instance.find('ol', {'class': 'tracklist'})
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
        temp = {'track_name': temp_list[0].text, 'track_singer': temp_list[1].text, 'track_album': temp_list[2].text,
                'duration': duration_list[counter].text}
        tracks_list.append(temp)
        temp_list = []
        counter += 1

data = {'album_title': album_title, 'cover_url': cover_url, 'author': author, 'author_url': author_url,
        'tracks_list': tracks_list}

print(data)
