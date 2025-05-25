# PyPI Deployment Instructions

## Current Status
✅ **Tests**: All unit tests are passing (17/17 core scraper tests pass)
✅ **Workflow**: Updated to use token-based authentication instead of trusted publishing
❌ **Secret**: Missing PYPI_API_TOKEN in repository secrets

## Required Actions

### 1. Add PyPI API Token to GitHub Secrets

You need to manually add the PyPI API token to your repository:

1. Go to your PyPI account at https://pypi.org/
2. Navigate to Account Settings → API tokens
3. Create a new API token:
   - Token name: `github-actions-spotifyscraper`
   - Scope: Project (spotify-scraper) or Entire account
4. Copy the token (starts with `pypi-`)
5. Add to GitHub repository:
   ```
   gh secret set PYPI_API_TOKEN --body="YOUR_PYPI_TOKEN_HERE"
   ```
   Or manually:
   - Go to: https://github.com/AliAkhtari78/SpotifyScraper/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token

### 2. Alternative: Configure Trusted Publishing (Recommended)

For better security, configure trusted publishing on PyPI:

1. Go to https://pypi.org/manage/project/spotify-scraper/settings/publishing/
2. Add a new publisher:
   - Owner: `AliAkhtari78`
   - Repository: `SpotifyScraper`
   - Workflow name: `publish.yml`
   - Environment: `pypi`

Then revert the workflow to use trusted publishing by uncommenting the original section.

## Deployment Process

Once the secret is added, deployment will work automatically:

1. **Manual deployment**: 
   ```bash
   gh workflow run publish.yml
   ```

2. **Release deployment**: Create a new release on GitHub

## Current Package Status

- Version: 2.0.1 (built and ready)
- Location: `dist/` directory
- Files:
  - `spotifyscraper-2.0.1-py3-none-any.whl`
  - `spotifyscraper-2.0.1.tar.gz`