# GitHub Pages Fix Instructions

The GitHub Pages build is failing because it's trying to process Python files. To fix this:

## Option 1: Change GitHub Pages Source (Recommended)

1. Go to: https://github.com/AliAkhtari78/SpotifyScraper/settings/pages
2. Under "Source", change from:
   - Branch: `master` 
   - Folder: `/ (root)`
3. To:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
4. Click "Save"

The `gh-pages` branch has been created with only a minimal redirect page to ReadTheDocs.

## Option 2: Disable GitHub Pages

If you don't need GitHub Pages (since documentation is on ReadTheDocs):

1. Go to: https://github.com/AliAkhtari78/SpotifyScraper/settings/pages
2. Look for an option to disable GitHub Pages
3. Or change the source to "None" if available

## Why This Is Happening

GitHub Pages is trying to build the site using Jekyll from the master branch, which includes all Python source files. The build fails when it tries to process these files. The gh-pages branch contains only a simple HTML redirect page, which will build successfully.

## Result

After making this change, the "pages build and deployment" workflow should succeed, and https://aliakhtari78.github.io/SpotifyScraper/ will redirect to the ReadTheDocs documentation.