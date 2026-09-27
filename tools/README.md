# tools/

Scripts that generate site images. Excluded from the published site (`_config.yml`).

## Title cards (article covers)

Every article cover is a title card in the style of the first article’s: kicker, title in Source Serif 4, name and tagline, domain, and the credit line `Pablo Correa Prieto · <year> · CC BY 4.0` bottom right. 1800×945.

1. Copy a file in `title-card/cards/` and edit it (one JSON per language). Name the output `pablo-correa-prieto-<topic-slug>-titre-<fr|en|es>.jpg`.
2. Render:

   ```sh
   node tools/title-card/render.mjs tools/title-card/cards/<topic>-titre-{fr,en,es}.json
   ```

3. Embed metadata (description = the image’s `alt` text on the page):

   ```sh
   tools/tag-image.sh pablo-correa-prieto-<topic-slug>-titre-fr.jpg 2026 fr "<alt text>"
   ```

4. Open each output and check it visually.

`render.mjs` needs Playwright with Chromium (preinstalled in the Claude Code cloud environment). The fonts are bundled in `title-card/fonts/` (SIL Open Font License, see the licence files there), so the output doesn’t depend on the network.

## Metadata

`tag-image.sh` embeds Creator, Credit Line, Copyright Notice, Web Statement of Rights (CC BY 4.0) and the licensor URL (the figure-reuse page for that language). Use it only on figures and covers Pablo made or confirmed as his — never on photos of him. Needs `exiftool`.

## Existing images

- `pablo-correa-prieto-ia-enseignant-titre-*.jpg`: rendered from `title-card/cards/ia-enseignant-titre-*.json`.
- `pablo-correa-prieto-ia-enseignant-deplacements-*.jpg`: no source file (made before this folder existed); the credit line was added on top of the original JPG.
