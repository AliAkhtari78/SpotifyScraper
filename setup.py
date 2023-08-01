from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='spotifyscraper',
    version='1.0.5',
    description='Spotify Web Player Scraper using python, scrape and download song and cover from Spotify.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AliAkhtari78/SpotifyScraper',
    author='Ali Akhtari',
    packages=["SpotifyScraper"],
    author_email='aliakhtari78@hotmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='spotify spotifydownloader downloader mp3downloader webscraper spotifywebscraper spotifyscraper music cover setuptools development',
    python_requires='>=3.6',
    install_requires=['appdirs',
                      'beautifulsoup4',
                      'bs4',
                      'certifi',
                      'chardet',
                      'cssselect',
                      'deprecation',
                      'eyeD3',
                      'fake-useragent',
                      'filetype',
                      'idna',
                      'lxml',
                      'packaging',
                      'parse',
                      'pyee',
                      'pyparsing',
                      'pyppeteer',
                      'pyquery',
                      'PyYAML',
                      'requests',
                      'six',
                      'soupsieve',
                      'tqdm',
                      'urllib3',
                      'w3lib',
                      'websockets',
                      ],

    project_urls={
        'Bug Reports': 'https://github.com/AliAkhtari78/SpotifyScraper/issues',
        'Source': 'https://github.com/AliAkhtari78/SpotifyScraper',
        'PyPi': 'https://pypi.org/project/spotifyscraper',
        'Documentation': 'https://spotifyscraper.readthedocs.io/en/latest',
        'Full Tutorial Blog': 'https://aliakhtari.com/Blog/SpotifyScraper',
        'Author WebSite': 'https://aliakhtari.com',
    },
)
