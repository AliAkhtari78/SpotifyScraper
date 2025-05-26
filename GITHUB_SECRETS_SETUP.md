# GitHub Secrets Setup Guide

This guide explains how to set up the required and optional GitHub secrets for this repository.

## Required Secrets

### 1. PYPI_API_TOKEN (Already configured ✓)
- **Purpose**: Publishing packages to PyPI
- **Status**: Already configured

### 2. ANTHROPIC_API_KEY (Already configured ✓)
- **Purpose**: Claude AI assistant integration
- **Status**: Already configured

## Optional Secrets (Add for Full Functionality)

### 3. CODECOV_TOKEN
- **Purpose**: Upload code coverage reports to Codecov
- **How to get**: 
  1. Go to https://codecov.io/
  2. Sign in with GitHub
  3. Add your repository
  4. Copy the upload token
- **Add to GitHub**: Settings → Secrets → Actions → New repository secret
- **Name**: `CODECOV_TOKEN`

### 4. TEST_PYPI_TOKEN
- **Purpose**: Testing package uploads before production
- **How to get**:
  1. Go to https://test.pypi.org/
  2. Register/Login
  3. Go to Account Settings → API tokens
  4. Create new token with scope "Entire account"
- **Add to GitHub**: Settings → Secrets → Actions → New repository secret
- **Name**: `TEST_PYPI_TOKEN`

### 5. DOCKERHUB_USERNAME and DOCKERHUB_TOKEN
- **Purpose**: Publishing Docker images to Docker Hub
- **How to get**:
  1. Go to https://hub.docker.com/
  2. Sign in or create account
  3. Go to Account Settings → Security → New Access Token
  4. Create token with "Read, Write, Delete" permissions
- **Add to GitHub**: 
  - Settings → Secrets → Actions → New repository secret
  - Name: `DOCKERHUB_USERNAME` (your Docker Hub username)
  - Name: `DOCKERHUB_TOKEN` (the access token you created)

### 6. READTHEDOCS_TOKEN
- **Purpose**: Trigger documentation builds on ReadTheDocs
- **How to get**:
  1. Go to https://readthedocs.org/
  2. Import your project if not already done
  3. Go to project settings → API Tokens
  4. Create new token
- **Add to GitHub**: Settings → Secrets → Actions → New repository secret
- **Name**: `READTHEDOCS_TOKEN`

### 7. Spotify Test IDs (Optional)
- **Purpose**: Integration testing with real Spotify data
- **Default values are provided if not set**:
  - `SPOTIFY_TEST_TRACK_ID`: "3n3Ppam7vgaVa1iaRUc9Lp" (Mr. Brightside)
  - `SPOTIFY_TEST_ALBUM_ID`: "1mSCXPEknPLQ8yuhM3SYxH" (Hot Fuss)
  - `SPOTIFY_TEST_ARTIST_ID`: "0C0XlULifJtAgn6ZNCW2eu" (The Killers)
  - `SPOTIFY_TEST_PLAYLIST_ID`: "37i9dQZF1DXcBWIGoYBM5M" (Today's Top Hits)

## How to Add Secrets

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Enter the secret name (exactly as shown above)
6. Enter the secret value
7. Click "Add secret"

## Verification

After adding secrets, you can verify they're working by:
1. Going to the "Actions" tab
2. Clicking "Manual Test" workflow
3. Running the workflow manually
4. Checking the logs for any warnings about missing secrets

## Notes

- All workflows are configured to handle missing optional secrets gracefully
- Missing secrets will show warnings but won't fail the workflows
- The repository will function without optional secrets, but with reduced features