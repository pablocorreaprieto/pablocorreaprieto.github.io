# pablocorreaprieto.ch

Personal site of Pablo Correa Prieto. Hand-written static HTML served by GitHub Pages from `main`, on the custom domain in `CNAME`. No build step: each page is a self-contained `.html` file with its own inline CSS and JSON-LD.

## Structure

French is the default language at the root; English lives in `/en/`, Spanish in `/es/`.

| Page | FR | EN | ES |
|---|---|---|---|
| Home / CV | `index.html` | `en/index.html` | `es/index.html` |
| Research project | `recherche.html` | `en/research.html` | `es/investigacion.html` |
| Publications | `publications.html` | `en/publications.html` | `es/publicaciones.html` |
| Article (24 Sept 2026) | `ia-enseignant-preparer-evaluer.html` | `en/ai-teachers-prepare-assess.html` | `es/ia-docente-preparar-evaluar.html` |
| Article: marking with AI (28 Sept 2026) | `ia-correction-second-regard.html` | `en/ai-marking-second-reader.html` | `es/ia-correccion-segunda-mirada.html` |
| Article: three questions for an item (28 Sept 2026) | `items-evaluation-trois-questions.html` | `en/assessment-items-three-questions.html` | `es/items-evaluacion-tres-preguntas.html` |
| Article: protect the effort (28 Sept 2026) | `ia-proteger-effort-apprendre.html` | `en/ai-protect-effort-learning.html` | `es/ia-proteger-esfuerzo-aprender.html` |
| Article: preparing with AI, checking (28 Sept 2026) | `remplacant-preparer-ia-verifier.html` | `en/substitute-teacher-ai-check-first.html` | `es/sustituto-preparar-ia-verificar.html` |
| Articles index | `articles.html` | `en/articles.html` | `es/articulos.html` |
| Figure reuse (licence) | `reutilisation-figures.html` | `en/figure-reuse.html` | `es/reutilizacion-figuras.html` |

Other files:

- `404.html` – trilingual “page not found”, served by GitHub Pages for any unknown URL.
- `sitemap.xml` – every page with its language alternates and images.
- `robots.txt`, `CNAME`, `google…html` (Search Console verification – do not delete).
- `favicon.*`, `apple-touch-icon.png` – icons.
- `logo-mark.svg` – the wordmark shown on the home pages, loaded with `<svg><use href="/logo-mark.svg#m"/></svg>` so it inherits the page’s text colour (light, dark and print). External `<use>` does not work when a page is opened as a local file; preview with a local server (`python3 -m http.server`) instead.
- `pablo-correa-prieto-*.jpg`, `pablo-correa-prieto-*.png` – article covers (JPG) and figures (PNG), one per language.
- `tools/` – scripts that generate article covers and figures and embed image metadata (see `tools/README.md`). Not published.
- `_config.yml` – keeps `README.md`, `CLAUDE.md` and `tools/` out of the published site.

URLs are extensionless (`/recherche`, not `/recherche.html`); GitHub Pages resolves them.

## Editing checklist

When you change a page:

1. Make the same change in all three languages.
2. Update the “Mis à jour / Updated / Actualizado” line in the footer if the month changed.
3. **Update `<lastmod>` in `sitemap.xml`** for every URL you changed (format `YYYY-MM-DD`). Search engines use it to decide what to re-crawl, so leaving old dates in place slows down indexing of your edits.

When you add a page, also:

1. Create all three language versions.
2. In each version’s `<head>`: `canonical`, the four `hreflang` alternates (fr, en, es, x-default → FR), `og:*` tags and JSON-LD.
3. Update the FR/EN/ES switcher in each version to point at its siblings.
4. Add three `<url>` entries to `sitemap.xml`, each listing all alternates and its images.
5. Link to it from the relevant home pages.
