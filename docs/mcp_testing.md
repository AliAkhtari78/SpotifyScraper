# MCP Testing Guide for SpotifyScraper

## Introduction

This guide explains how to use MCP (Mock, Capture, Playback) testing with SpotifyScraper to create reliable, reproducible tests that don't depend on network access or Spotify's availability.

## What is MCP Testing?

MCP testing is a three-phase approach to testing network-dependent code:

1. **Mock** - Create realistic simulations of network responses
2. **Capture** - Record real HTTP interactions for future use
3. **Playback** - Replay recorded responses during tests

This approach offers several benefits:
- Tests run faster after the initial recording
- Tests are deterministic and don't depend on network conditions
- Tests aren't affected by rate limiting or service changes
- Real data is used for validation, ensuring accurate testing

## Implementation Details

SpotifyScraper's MCP testing uses [VCR.py](https://vcrpy.readthedocs.io/), a library that records HTTP interactions and saves them as "cassettes" (YAML files) that can be replayed in future test runs.

### Key Components

1. **VCR Configuration**: Found in `tests/unit/test_track_album_mcp.py`
2. **Cassettes Directory**: `tests/fixtures/vcr_cassettes/`
3. **Test Runner**: `mcp_test_runner.py` for easy execution of MCP tests
4. **Example Script**: `examples/mcp_testing_demo.py` demonstrating usage

## Using MCP Testing

### Running MCP Tests

```bash
# Run all MCP tests
python mcp_test_runner.py

# Force recording new cassettes
python mcp_test_runner.py --record

# Delete existing cassettes and record new ones
python mcp_test_runner.py --clean --record

# Run a specific MCP test file
pytest tests/unit/test_track_album_mcp.py -v
```

### Creating New MCP Tests

1. Create a test file in `tests/unit/` with a name containing "mcp"
2. Import and configure VCR:

```python
import vcr
from pathlib import Path

# Configure VCR
vcr_cassette_dir = Path(__file__).parent.parent / "fixtures" / "vcr_cassettes"
my_vcr = vcr.VCR(
    cassette_library_dir=str(vcr_cassette_dir),
    record_mode='once',
    match_on=['uri', 'method'],
    filter_headers=['authorization', 'cookie'],
)
```

3. Create test methods with the `@my_vcr.use_cassette()` decorator:

```python
@my_vcr.use_cassette('my_test_cassette.yaml')
def test_some_network_functionality(self):
    # This test will record HTTP interactions the first time
    # and replay them in subsequent runs
    client = SpotifyClient()
    data = client.get_track_info("https://open.spotify.com/track/12345")
    assert "album" in data
```

## Demo and Examples

The `examples/mcp_testing_demo.py` script demonstrates:

1. Extracting album data from JSON-LD content
2. Working with track data that includes album information
3. The overall MCP testing approach

Run it with:

```bash
python examples/mcp_testing_demo.py
```

## Testing the JSON-LD Fallback

One key feature tested with MCP is the JSON-LD fallback mechanism for album data:

1. If the primary extraction method doesn't provide album data, the code tries to extract it from JSON-LD
2. JSON-LD is embedded in track pages for SEO purposes and often contains album information
3. The `extract_album_data_from_jsonld()` function parses this data into the standardized album format

The MCP tests verify that:
- The JSON-LD extraction works correctly
- The fallback logic properly integrates extracted album data
- The final track data includes the album field

## Best Practices

1. **Filter sensitive information**: Use VCR's filtering options to avoid recording cookies or API keys
2. **Use deterministic URLs**: Avoid using random parameters in URLs
3. **Keep cassettes up to date**: Periodically re-record cassettes to match current API behavior
4. **Commit cassettes to version control**: This ensures consistent test behavior
5. **Document unusual behavior**: Note any quirks in cassettes for future reference

## Troubleshooting

- **Cassette not found**: Ensure the cassette exists or run with `--record`
- **Unexpected behavior**: Try deleting the cassette and re-recording
- **Authentication issues**: Check if your tests require authentication
- **Match errors**: VCR may fail to match requests if URLs or request bodies change

## Resources

- [VCR.py Documentation](https://vcrpy.readthedocs.io/)
- [SpotifyScraper Documentation](https://spotifyscraper.readthedocs.io/)
- [README_TESTING.md](README_TESTING.md) - General testing guide for SpotifyScraper