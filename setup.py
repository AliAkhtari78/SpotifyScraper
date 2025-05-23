"""
Setup script for SpotifyScraper package.
Modern Python package configuration with updated dependencies.
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Get package directory
here = Path(__file__).parent.absolute()
src_dir = here / 'src'
package_dir = src_dir / 'spotify_scraper'

# Get version from package __init__.py
version_file = package_dir / '__init__.py'
if version_file.exists():
    version_content = version_file.read_text(encoding='utf-8')
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", version_content, re.MULTILINE)
    if version_match:
        version = version_match.group(1)
    else:
        version = "2.0.0"  # Fallback version
else:
    version = "2.0.0"  # Fallback version

# Get long description from README
readme_file = here / 'README.md'
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')
else:
    long_description = "A modern Python library for extracting data from Spotify's web interface."

# Core dependencies
install_requires = [
    # Core web scraping
    'beautifulsoup4',
    'lxml',
    'requests',
    'urllib3',

    # HTML/XML parsing
    'cssselect',
    'soupsieve',

    # Media processing
    'eyeD3',
    'filetype',

    # Network utilities
    'fake-useragent',
    'certifi',

    # Configuration and data
    'PyYAML',
    'packaging',
    'tqdm',

    # Parsing utilities
    'pyparsing',
    'deprecation',
]

# Optional dependencies
extras_require = {
    'selenium': [
        'selenium',
    ],
    'async': [
        'pyppeteer',
        'pyee',
        'websockets',
    ],
    'dev': [
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'black',
        'isort',
        'flake8',
        'mypy',
        'pre-commit',
    ],
    'docs': [
        'sphinx',
        'sphinx-rtd-theme',
        'myst-parser',
    ],
    'all': [
        'selenium',
        'pyppeteer',
        'pyee',
        'websockets',
    ],
}

setup(
    name='spotifyscraper',
    version=version,
    description='A modern Python library for extracting data from Spotify\'s web interface without using the official API',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # Author and license
    author='Ali Akhtari',
    author_email='aliakhtari78@hotmail.com',
    license='MIT',

    # URLs
    url='https://github.com/AliAkhtari78/SpotifyScraper',
    project_urls={
        'Bug Reports': 'https://github.com/AliAkhtari78/SpotifyScraper/issues',
        'Source': 'https://github.com/AliAkhtari78/SpotifyScraper',
        'Documentation': 'https://spotifyscraper.readthedocs.io/',
        'Changelog': 'https://github.com/AliAkhtari78/SpotifyScraper/blob/main/CHANGELOG.md',
    },

    # Package discovery
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,

    # Requirements
    python_requires='>=3.8',
    install_requires=install_requires,
    extras_require=extras_require,

    # Classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords=[
        'spotify', 'scraper', 'scraping', 'web-scraping', 'downloader',
        'mp3', 'music', 'audio', 'cover', 'playlist', 'artist', 'album',
        'beautifulsoup4', 'selenium', 'requests', 'automation'
    ],

    # Entry points for CLI commands
    entry_points={
        'console_scripts': [
            'spotify-scraper=spotify_scraper.cli:main',
            'spotifyscraper=spotify_scraper.cli:main',  # Alternative name
        ],
    },

    # Package data
    package_data={
        'spotify_scraper': [
            'py.typed',  # Type hints marker
        ],
    },

    # Zip safety
    zip_safe=False,
)
