# Contributing to SpotifyScraper

First off, thank you for considering contributing to SpotifyScraper! It's people like you that make SpotifyScraper such a great tool. 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by the [SpotifyScraper Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [ali@aliakhtari.com](mailto:ali@aliakhtari.com).

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Add the upstream repository** as a remote
4. **Create a new branch** for your contribution

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SpotifyScraper.git
cd SpotifyScraper

# Add upstream repository
git remote add upstream https://github.com/AliAkhtari78/SpotifyScraper.git

# Create a new branch
git checkout -b feature/your-feature-name
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- git
- (Optional) pyenv for managing Python versions
- (Optional) Virtual environment tool (venv, virtualenv, or conda)

### Setting Up Your Environment

1. **Create a virtual environment** (recommended):

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n spotifyscraper python=3.10
conda activate spotifyscraper
```

2. **Install the package in development mode**:

```bash
# Install with all development dependencies
pip install -e ".[dev]"

# Or install specific extras
pip install -e ".[dev,selenium]"
```

3. **Verify your setup**:

```bash
# Run tests
pytest

# Check code formatting
black --check src/ tests/

# Run linting
flake8 src/ tests/
```

### Development Dependencies

The `[dev]` extra includes:

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatter
- **isort**: Import sorter
- **flake8**: Linting
- **mypy**: Type checking
- **sphinx**: Documentation
- **pre-commit**: Git hooks

## Making Changes

### Workflow

1. **Keep your fork up to date**:

```bash
git fetch upstream
git checkout master
git merge upstream/master
```

2. **Make your changes**:
   - Write clean, readable code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_track_extractor.py

# Run with coverage
pytest --cov=spotify_scraper --cov-report=html
```

### Guidelines

- **One pull request per feature**: Don't mix unrelated changes
- **Write meaningful commit messages**: Use the present tense ("Add feature" not "Added feature")
- **Update the CHANGELOG**: Add your changes under the "Unreleased" section
- **Add tests**: Aim for 100% coverage of new code
- **Document your code**: Use docstrings and type hints

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Test additions or modifications
- **chore**: Maintenance tasks

Example:
```
feat: add support for podcast extraction

- Implement PodcastExtractor class
- Add tests for podcast parsing
- Update CLI to handle podcast URLs

Closes #123
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_client.py

# Run tests matching a pattern
pytest -k "test_track"

# Run with coverage
pytest --cov=spotify_scraper --cov-report=term-missing
```

### Writing Tests

1. **Location**: Place tests in the appropriate directory:
   - `tests/unit/` for unit tests
   - `tests/integration/` for integration tests

2. **Naming**: Use descriptive test names:
   ```python
   def test_track_extractor_parses_valid_json():
       # Test implementation
   ```

3. **Structure**: Use the Arrange-Act-Assert pattern:
   ```python
   def test_download_preview():
       # Arrange
       client = SpotifyClient()
       track_id = "6rqhFgbbKwnb9MLmUQDhG6"
       
       # Act
       result = client.download_preview(track_id)
       
       # Assert
       assert Path(result).exists()
       assert result.endswith(".mp3")
   ```

4. **Fixtures**: Use pytest fixtures for common setup:
   ```python
   @pytest.fixture
   def mock_client():
       return SpotifyClient(timeout=5)
   ```

### Test Coverage

We aim for high test coverage. Check coverage with:

```bash
# Generate coverage report
pytest --cov=spotify_scraper --cov-report=html

# View HTML report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

## Code Style

### Formatting

We use **black** for code formatting and **isort** for import sorting:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check without modifying
black --check src/ tests/
isort --check-only src/ tests/
```

### Linting

We use **flake8** for linting and **mypy** for type checking:

```bash
# Run flake8
flake8 src/ tests/

# Run mypy
mypy src/

# Run pylint (optional, more strict)
pylint src/
```

### Style Guidelines

1. **Follow PEP 8**: With black's formatting
2. **Use type hints**: For all public functions and methods
3. **Write docstrings**: For all public modules, classes, and functions
4. **Keep it simple**: Favor readability over cleverness
5. **Use meaningful names**: Variables and functions should be self-documenting

Example:
```python
from typing import Dict, Optional

def get_track_metadata(track_id: str, include_lyrics: bool = False) -> Dict[str, Any]:
    """Extract metadata for a Spotify track.
    
    Args:
        track_id: The Spotify track ID
        include_lyrics: Whether to include lyrics (requires auth)
        
    Returns:
        Dictionary containing track metadata
        
    Raises:
        TrackNotFoundError: If the track doesn't exist
        AuthenticationError: If lyrics requested without auth
    """
    # Implementation
```

### Pre-commit Hooks

We recommend using pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Submitting Changes

### Pull Request Process

1. **Update your branch** with the latest upstream changes
2. **Run all tests** and ensure they pass
3. **Update documentation** if needed
4. **Add a changelog entry** under "Unreleased"
5. **Push to your fork** and create a pull request

### Pull Request Template

When creating a PR, please include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] All tests pass locally
- [ ] Added new tests for new functionality
- [ ] Updated existing tests as needed

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
```

### Review Process

1. **Automated checks**: CI will run tests, linting, and coverage
2. **Code review**: Maintainers will review your code
3. **Feedback**: Address any comments or requested changes
4. **Merge**: Once approved, your PR will be merged

## Reporting Issues

### Before Submitting an Issue

1. **Check existing issues**: Your issue might already be reported
2. **Check the FAQ**: Common problems might be addressed there
3. **Try the latest version**: Update to the latest release
4. **Gather information**: Prepare error messages, logs, and system info

### Issue Template

```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. First step
2. Second step
3. ...

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- SpotifyScraper version:
- Python version:
- Operating System:
- Browser backend (if applicable):

## Additional Context
Any other relevant information, logs, or screenshots
```

## Feature Requests

We love hearing new ideas! When requesting a feature:

1. **Check existing requests**: It might already be planned
2. **Be specific**: Clearly describe the feature and use case
3. **Consider implementation**: Think about how it might work
4. **Be patient**: Features take time to implement properly

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why this feature would be useful

## Proposed Implementation
How you think this could work (optional)

## Alternatives Considered
Other ways to achieve the same goal

## Additional Context
Any mockups, examples, or references
```

## Community

### Getting Help

- **Documentation**: [Read the Docs](https://spotifyscraper.readthedocs.io/)
- **GitHub Discussions**: Ask questions and share ideas
- **Stack Overflow**: Tag questions with `spotifyscraper`
- **Discord**: Join our [community server](https://discord.gg/spotifyscraper)

### Ways to Contribute

Not just code! You can help by:

- **Testing**: Try new releases and report issues
- **Documentation**: Fix typos, improve clarity, add examples
- **Translations**: Help translate documentation
- **Support**: Answer questions in discussions
- **Promotion**: Write blog posts, create tutorials

### Recognition

Contributors are recognized in:
- The [Contributors](https://github.com/AliAkhtari78/SpotifyScraper/graphs/contributors) page
- Release notes for significant contributions
- The project README for major features

## Questions?

Feel free to:
- Open a [GitHub Discussion](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
- Email the maintainer at [ali@aliakhtari.com](mailto:ali@aliakhtari.com)
- Ask in our [Discord server](https://discord.gg/spotifyscraper)

Thank you for contributing to SpotifyScraper! 🎵✨