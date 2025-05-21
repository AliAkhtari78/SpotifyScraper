"""
Setup script for SpotifyScraper package.
"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get version from package
with open(path.join(here, 'src', 'spotify_scraper', '__init__.py'), encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

# Get long description from README
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='spotifyscraper',
    version=version,
    description='Spotify Web Player Scraper using Python - extract data and download content from Spotify',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AliAkhtari78/SpotifyScraper',
    author='Ali Akhtari',
    author_email='aliakhtari78@hotmail.com',
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    
    keywords='spotify scraper downloader mp3 webscraper spotifywebscraper music cover playlist artist album',
    
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8',
    
    install_requires=[
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0',
        'lxml>=4.9.0',
        'pyyaml>=6.0',
        'eyeD3>=0.9.5',
    ],
    
    extras_require={
        'selenium': ['selenium>=4.0.0'],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.0.0',
            'mypy>=1.0.0',
            'pylint>=2.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    
    project_urls={
        'Bug Reports': 'https://github.com/AliAkhtari78/SpotifyScraper/issues',
        'Source': 'https://github.com/AliAkhtari78/SpotifyScraper',
        'Documentation': 'https://spotifyscraper.readthedocs.io/',
    },
)
