# Post-Release Checklist for v2.1.3

## GitHub Actions Status
Monitor the CI/CD pipeline at: https://github.com/AliAkhtari78/SpotifyScraper/actions

Expected to pass:
- ✅ Black formatting
- ✅ isort import sorting  
- ✅ Flake8 linting
- ✅ Pylint (9.96/10)
- ✅ MyPy type checking
- ✅ Unit tests

## Documentation Updates

### 1. GitHub Wiki
The Wiki pages in the `wiki/` directory have been updated. To update the GitHub Wiki:

1. Go to: https://github.com/AliAkhtari78/SpotifyScraper/wiki
2. Update each page with content from the corresponding file in `wiki/`:
   - Home.md
   - Installation.md
   - Quick-Start.md
   - Examples.md
   - API-Reference.md
   - FAQ.md

### 2. ReadTheDocs (MkDocs)
The MkDocs documentation will automatically rebuild when pushed to GitHub.

Check status at: https://spotifyscraper.readthedocs.io/

If manual build needed:
1. Log into ReadTheDocs
2. Go to SpotifyScraper project
3. Click "Build Version"

### 3. PyPI Release

To publish v2.1.3 to PyPI:

```bash
# The package is already built in dist/
# spotifyscraper-2.1.3-py3-none-any.whl
# spotifyscraper-2.1.3.tar.gz

# Upload to PyPI (requires PyPI token)
python -m twine upload dist/spotifyscraper-2.1.3*
```

Or use GitHub Actions:
1. Add PYPI_API_TOKEN to repository secrets
2. Create a GitHub Release tagged v2.1.3
3. The publish workflow will automatically upload to PyPI

## Verification Steps

After all updates:

1. **Test Installation**:
   ```bash
   pip install spotifyscraper==2.1.3
   ```

2. **Verify Documentation**:
   - Check ReadTheDocs shows updated examples
   - Verify GitHub Wiki has correct code
   - Confirm PyPI page shows new version

3. **Test Basic Functionality**:
   ```python
   from spotify_scraper import SpotifyClient
   client = SpotifyClient()
   track = client.get_track_info("spotify_track_url")
   print(track['name'])
   ```

## Key Changes to Communicate

When announcing the release:

1. **Breaking Change**: Error handling now raises exceptions instead of returning error dicts
2. **OAuth Required for Lyrics**: Cookie authentication alone is insufficient
3. **Improved Documentation**: All examples updated to use only available fields
4. **Better Error Messages**: Clear indication when OAuth is required

## Support

If users report issues:
1. Check they're using v2.1.3: `pip show spotifyscraper`
2. Verify they're catching exceptions properly (not checking for error dicts)
3. For lyrics issues, explain OAuth requirement
4. Direct to updated documentation