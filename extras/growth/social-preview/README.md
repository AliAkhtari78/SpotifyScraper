# Social preview image

GitHub renders a repo's "social preview" card on Twitter/X, Slack, Discord,
LinkedIn, etc. This repo doesn't have one yet — adding it lifts click-through on
**every** shared link (launch posts, directory listings, the author site).

## Steps

1. Export `social-preview.svg` to a **1280×640 PNG**. Any of:
   - Open the SVG in a browser, screenshot at 1280×640; or
   - `rsvg-convert -w 1280 -h 640 social-preview.svg -o social-preview.png`; or
   - `inkscape social-preview.svg --export-type=png -w 1280 -h 640`; or
   - macOS Quick Look / Preview → export as PNG.
2. GitHub → repo **Settings** → **Social preview** → **Edit** → upload the PNG.

Tweak colors/copy in the SVG first if you want — it's plain text. Keep the
1280×640 aspect ratio (GitHub crops other sizes).
