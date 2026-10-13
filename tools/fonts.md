# Self-hosted fonts

`assets/fonts/` holds the site's two typefaces as variable WOFF2 files,
declared in `assets/fonts.css` and preloaded from every page. No page may
load fonts from Google (`fonts.googleapis.com` / `fonts.gstatic.com`): the
site makes no third-party requests.

## Provenance

- **Source Serif 4** — SIL OFL 1.1, Adobe. From npm package
  `@fontsource-variable/source-serif-4` **5.3.1**, files
  `source-serif-4-latin{,-ext}-opsz-{normal,italic}.woff2`
  (axes `wght` + `opsz 8–60`).
- **IBM Plex Sans** — SIL OFL 1.1, IBM. From npm package
  `@fontsource-variable/ibm-plex-sans` **5.3.0**, files
  `ibm-plex-sans-latin{,-ext}-wght-normal.woff2` (axis `wght`).

Both were instanced to the weight range the site uses, which is what makes
the files smaller than the upstream ones:

```sh
npm install @fontsource-variable/source-serif-4@5.3.1 @fontsource-variable/ibm-plex-sans@5.3.0
pip install fonttools brotli
fonttools varLib.instancer -o out.woff2 <upstream.woff2> wght=400:600
```

The `@font-face` rules in `assets/fonts.css` keep the upstream `unicode-range`
values for the latin and latin-ext subsets and declare the families under the
names the pages' CSS variables expect (`"Source Serif 4"`, `"IBM Plex Sans"`),
`font-weight: 400 600`, `font-display: swap`. Source Serif's optical size
applies automatically (`font-optical-sizing: auto` is the browser default).

## If a weight or style is ever needed outside 400–600

Re-run the instancer with a wider `wght` range (or ship the upstream file
unchanged) and update the `font-weight` ranges in `assets/fonts.css`.
IBM Plex Sans italic is not shipped because no page requests it; browsers
synthesise it, as they already did when the fonts came from Google.
