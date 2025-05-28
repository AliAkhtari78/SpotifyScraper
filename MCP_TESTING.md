# MCP Testing for SpotifyScraper

## Overview

MCP (Mock, Capture, Playback) testing is a powerful approach for testing network-dependent code. It allows developers to:

1. **Capture real HTTP interactions** during an initial test run
2. **Replay those interactions** in future test runs without making real network requests
3. **Validate code changes** against real-world data without requiring constant network access

This approach provides several benefits:
- Tests run faster after initial recording
- Tests are deterministic and don't depend on network conditions
- Tests don't get affected by rate limiting or service changes
- Real data is used for validation, ensuring accurate testing

## How It Works

SpotifyScraper's MCP testing uses [VCR.py](https://vcrpy.readthedocs.io/), a library that records HTTP interactions and saves them as "cassettes" (YAML files) that can be replayed in future test runs.

The process works as follows:

1. When a test is run for the first time, VCR.py records all HTTP requests and responses
2. These recordings are saved as cassettes in the `tests/fixtures/vcr_cassettes` directory
3. On subsequent test runs, VCR.py intercepts HTTP requests and returns the recorded responses

## Running MCP Tests

### Prerequisites

```bash
pip install vcrpy
```

### Basic Usage

```bash
# Run MCP tests using existing cassettes
python mcp_test_runner.py
```

### Recording New Cassettes

```bash
# Force recording new cassettes (overwrite existing ones)
python mcp_test_runner.py --record

# Delete all existing cassettes and record new ones
python mcp_test_runner.py --clean --record
```

### Running Specific Tests

```bash
# Run specific MCP tests directly with pytest
pytest tests/unit/test_track_album_mcp.py -v
```

## Creating New MCP Tests

1. Create a new test file in `tests/unit/` with a name containing "mcp"
2. Import vcr and configure it with appropriate settings
3. Use the `@my_vcr.use_cassette()` decorator on your test functions
4. Run your tests with the `--record` flag to generate cassettes

Example:

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

class TestExample:
    @my_vcr.use_cassette('example_test.yaml')
    def test_something_with_network_requests(self):
        # This test will record HTTP interactions the first time
        # and replay them in subsequent runs
        ...
```

## Best Practices

1. **Filter sensitive information**: Use VCR's filtering options to avoid recording sensitive data like cookies or API keys
2. **Use deterministic URLs**: Avoid using random parameters in URLs that would cause VCR to miss cassette matches
3. **Keep cassettes up to date**: Periodically re-record cassettes to ensure they match current API behavior
4. **Commit cassettes to version control**: This ensures consistent test behavior across different environments
5. **Handle authentication**: For tests requiring authentication, use environment variables or mock credentials

## Troubleshooting

- **Cassette not found**: Ensure the cassette exists in the specified directory or run with `--record`
- **Unexpected behavior**: Try deleting the cassette and re-recording with `--clean --record`
- **Authentication issues**: Check if your tests require authentication and how it's being handled
- **Match errors**: VCR may fail to match requests if URLs or request bodies change. Check your matching configuration.

## References

- [VCR.py Documentation](https://vcrpy.readthedocs.io/)
- [SpotifyScraper Testing Guide](README_TESTING.md)