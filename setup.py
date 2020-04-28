from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='spotifyscraper',
    version='1.0.0',
    description='A sample Python project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/sampleproject',
    author='The Python Packaging Authority',
    packages=["SpotifyScraper"],
    author_email='pypa-dev@googlegroups.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='spotify spotifydownloader downloader mp3downloader webscraper spotifyscraper music cover setuptools development',
    python_requires='>=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
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
                      ],  # Optional

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/pypa/sampleproject/',
    },
)
