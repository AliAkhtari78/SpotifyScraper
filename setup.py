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
    'beautifulsoup4>=4.13.0,<5.0.0',
    'lxml>=5.3.0,<6.0.0',
    'requests>=2.32.0,<3.0.0',
    'urllib3>=2.3.0,<3.0.0',
    
    # HTML/XML parsing
    'cssselect>=1.2.0,<2.0.0',
    'soupsieve>=2.5.0,<3.0.0',
    
    # Media processing
    'eyeD3>=0.9.7,<1.0.0',
    'filetype>=1.2.0,<2.0.0',
    
    # Network utilities
    'fake-useragent>=1.5.0,<2.0.0',
    'certifi>=2024.2.2',
    
    # Configuration and data
    'PyYAML>=6.0.1,<7.0.0',
    'packaging>=24.0,<25.0.0',
    'tqdm>=4.66.0,<5.0.0',
    
    # Parsing utilities
    'pyparsing>=3.1.0,<4.0.0',
    'deprecation>=2.1.0,<3.0.0',
]

# Optional dependencies
extras_require = {
    'selenium': [
        'selenium>=4.30.0,<5.0.0',
    ],
    'async': [
        'pyppeteer>=2.0.0,<3.0.0',
        'pyee>=11.0.0,<12.0.0',
        'websockets>=12.0,<13.0.0',
    ],
    'dev': [
        'pytest>=8.0.0,<9.0.0',
        'pytest-asyncio>=0.23.0,<1.0.0',
        'pytest-cov>=4.0.0,<5.0.0',
        'black>=24.0.0,<25.0.0',
        'isort>=5.13.0,<6.0.0',
        'flake8>=7.0.0,<8.0.0',
        'mypy>=1.8.0,<2.0.0',
        'pre-commit>=3.6.0,<4.0.0',
    ],
    'docs': [
        'sphinx>=7.0.0,<8.0.0',
        'sphinx-rtd-theme>=2.0.0,<3.0.0',
        'myst-parser>=2.0.0,<3.0.0',
    ],
    'all': [
        'selenium>=4.30.0,<5.0.0',
        'pyppeteer>=2.0.0,<3.0.0',
        'pyee>=11.0.0,<12.0.0',
        'websockets>=12.0,<13.0.0',
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
        'beautifulsoup', 'selenium', 'requests', 'automation'
    ],
    
    # Entry points (if any CLI tools are added)
    entry_points={
        'console_scripts': [
            # 'spotifyscraper=spotify_scraper.cli:main',  # Uncomment if CLI is implemented
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
