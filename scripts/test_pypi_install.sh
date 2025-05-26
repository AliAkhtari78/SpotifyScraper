#!/bin/bash
# Test PyPI package installation

echo "🧪 Testing SpotifyScraper PyPI Installation"
echo "=========================================="

# Create a temporary virtual environment
TEMP_DIR=$(mktemp -d)
echo "📁 Creating temporary environment in: $TEMP_DIR"

cd "$TEMP_DIR"
python3 -m venv test_env
source test_env/bin/activate

echo -e "\n📦 Installing spotifyscraper from PyPI..."
pip install --no-cache-dir spotifyscraper 2>&1 | grep -E "Successfully installed|ERROR|Collecting spotifyscraper"

echo -e "\n🔍 Checking installed version..."
python -c "import spotify_scraper; print(f'Version: {spotify_scraper.__version__}')"

echo -e "\n✅ Testing basic imports..."
python -c "
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import create_browser
from spotify_scraper.extractors import TrackExtractor
print('All imports successful!')
"

echo -e "\n🖥️  Testing CLI availability..."
which spotifyscraper
spotifyscraper --version

echo -e "\n🧹 Cleaning up..."
deactivate
rm -rf "$TEMP_DIR"

echo -e "\n✅ Test complete!"