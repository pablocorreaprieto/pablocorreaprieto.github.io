# CLAUDE.md

Rules for working on pablocorreaprieto.ch. Structure and the page-editing checklist are in `README.md`; read it first.

## The site

Personal site of Pablo Correa Prieto (short form: Pablo Correa). Teacher in Vaud, master’s student in education research (UNIR), research interest: AI in education.

Readers: Vaud school directors, and researchers / doctoral supervisors. Neither should feel the page is written for someone else.

Articles are short, rigorous pieces on AI in education, each with original figures credited to Pablo, so that the site and its images come up when someone searches his name, including in Google Images.

## Non-negotiables

- **Nothing invented or inflated.** No claims about Pablo’s experience, roles, results, qualifications, publications or affiliations beyond what the site already states or he supplies in the conversation. This includes titles, dates, co-authors, venues, institutions, job titles and numbers.
- **Don’t upgrade status or wording:** “in preparation” is not “submitted” or “published”; a bachelor’s thesis (TFG) is a `Thesis`, not a `ScholarlyArticle`.
- **Dates** come from the site, from Pablo, or from git history — never estimated.
- **Citations:** only sources you have actually opened (the DOI resolves or the page loads). APA 7. If you can’t verify one, write `[SOURCE À VÉRIFIER]` and tell Pablo. Never invent authors, years, titles or pages.
- **No unpublished data or results** from Pablo’s studies; only what is already public.
- **Charts only from real, cited data.** Conceptual diagrams are fine.
- **Images:** no stock images, no photos of anyone except Pablo’s headshot, no AI-generated photorealistic images, no robot or glowing-brain clichés.
- **Credit and CC BY apply to figures and covers only**, and only to ones Pablo made or has confirmed as his — never to photos of Pablo.
- **Profiles:** link only the profiles listed under “Profiles”. Never Facebook or YouTube.
- **Placeholders:** where text is needed and the facts aren’t available, leave a visible placeholder like `[À COMPLÉTER : …]` and list every placeholder in the reply and the PR body. A PR with placeholders is not ready to merge; say so.
- **Structured data (JSON-LD)** describes only what the visible page says.
- **Never push to `main` and never merge.** Pablo merges. See “Git workflow”.

## Languages

- **French first.** French is the source language and lives at the root (`/`); English at `/en/`, Spanish at `/es/`.
- **EN and ES stay in sync with FR.** A change is not done until all three pages carry it: visible text, `<title>`, meta description, `og:*` tags, image alt text, figure labels, JSON-LD, the FR/EN/ES switcher and reciprocal `hreflang` (fr, en, es, x-default → fr). If a translation can’t be done yet, say so; don’t ship a partial set.
- EN and ES articles are adapted, not translated word for word.
- Content that exists in one language only (e.g. the LinkedIn version of the first article, French only) stays that way; don’t create links to non-existent versions.

## Workflow for each article

1. Ask Pablo for the topic, his angle (3–5 points in his own words) and any sources he wants used. **Don’t draft before you have his angle.**
2. Draft the French version: 700–1,200 words, plain and precise, no hype.
3. Make the images (see “Images”).
4. Show Pablo the draft and the images; wait for his edits.
5. Write the English and Spanish versions, with figure labels translated.
6. End every version with a one-line AI-assistance note:
   - FR: « Texte rédigé avec l’aide d’une IA, relu et validé par l’auteur. »
   - EN: “Text written with the help of AI, reviewed and approved by the author.”
   - ES: «Texto redactado con ayuda de una IA, revisado y validado por el autor.»
7. Run the checklist and preview locally (`python3 -m http.server`).
8. Push the branch and open or update the pull request. Pablo reviews and merges (“publish”).

## Images

Each article gets:

- **1–2 content figures** that explain something (model diagram, concept map, timeline, study design). SVG source in the repo, exported to PNG at least 1600 px wide; one PNG per language when the figure contains text.
- **1 cover per language:** a title card in the style of the first article’s (kicker, article title, Pablo’s name, the domain, plus the credit line), 1800×945, generated with `tools/title-card/` (see `tools/README.md`). It is the first image on the article page, the `og:image`, and the article’s image on the articles index.

For every image:

- Filename: `pablo-correa-prieto-<topic-slug>-<fr|en|es>.png`; covers: `pablo-correa-prieto-<topic-slug>-titre-<fr|en|es>.jpg`. Exception: the first article’s figures stay JPG (`pablo-correa-prieto-ia-enseignant-deplacements-<fr|en|es>.jpg`).
- Credit line inside the image, small, bottom right: `Pablo Correa Prieto · <year> · CC BY 4.0`.
- A real `<img>` inside `<figure>` (never a CSS background), with `width` and `height`; don’t lazy-load the first image on a page.
- `alt`: what the figure shows, in the page’s language. No keyword stuffing.
- `<figcaption>`: short description + `© Pablo Correa Prieto, <year> — CC BY 4.0`.
- Embedded metadata with `tools/tag-image.sh`: Creator, Credit Line, Copyright Notice, Web Statement of Rights (https://creativecommons.org/licenses/by/4.0/), licensor URL (the figure-reuse page).
- Open each exported PNG and check it visually before using it. Keep sources and scripts so every figure can be regenerated.

## Pages and structured data

- `<title>`: `<Article title> — Pablo Correa Prieto`. Visible byline and date.
- **Meta description: 160 characters or fewer**, in the page’s language. Count before committing. Shorten by cutting words or reusing wording already on the page; don’t add claims to fill space. Keep `og:description` identical unless the page deliberately differs (the home pages do).
- Base URL: `https://pablocorreaprieto.ch` (from `CNAME`).
- Home page: headshot near the top, next to the name (`pablo-correa-prieto.jpg`, alt “Pablo Correa Prieto”).
- Home page JSON-LD: `Person` with `@id` `https://pablocorreaprieto.ch/#person`, `name` “Pablo Correa Prieto”, `alternateName` “Pablo Correa”, `image` (headshot), `sameAs` (profiles below). Other pages reference this `@id`.
- Article JSON-LD: `Article` (for every article) with `author` → the Person `@id`, `headline`, `inLanguage`, `datePublished`, `image`; plus one `ImageObject` per figure with `contentUrl`, `creator`, `creditText`, `copyrightNotice`, `license`, `acquireLicensePage` (a short page explaining how to reuse Pablo’s figures).
- Open Graph and Twitter card tags using the cover.
- Figure-reuse page (`acquireLicensePage`): `/reutilisation-figures`, `/en/figure-reuse`, `/es/reutilizacion-figuras`. Figcaption credits link to it.
- An articles index page per language (`/articles`, `/en/articles`, `/es/articulos`), each article shown with its cover. Add every new article there and to the home pages’ Articles section.
- Non-site files (docs, `tools/`) are kept off the published site by `_config.yml` `exclude` (GitHub Pages runs Jekyll; there is no `.nojekyll`). Add any new non-site file or folder there.
- `sitemap.xml`: every page with its hreflang alternates and its images (`<image:image><image:loc>` only; the other image tags are deprecated). Update `<lastmod>` for every page you change. Referenced in `robots.txt`.

## Profiles

Only these may be linked (visible links or JSON-LD `sameAs`):

- ORCID: https://orcid.org/0009-0009-1844-7453
- OSF: https://osf.io/skvn4
- GitHub: https://github.com/pablocorreaprieto
- Google Scholar: https://scholar.google.com/citations?user=N2vtvGcAAAAJ
- LinkedIn: https://www.linkedin.com/in/pablocorreaprieto
- ResearchGate: https://www.researchgate.net/profile/Pablo-Correa-Prieto
- Academia.edu: https://universidadinternacionaldelarioja.academia.edu/PabloCorreaPrieto
- Wikidata: https://www.wikidata.org/wiki/Q141533563

HAL: none for now. Any other profile only after Pablo confirms its URL.

## Git workflow

- Work on a branch. Pushing working branches and opening or updating pull requests is always allowed (the cloud container is temporary, so push rather than leave commits only local).
- **Never push to `main` and never merge.** “Publish” means Pablo merges the pull request himself after review.
- Keep PRs focused, and describe every change and anything left open in the PR body.

## Checklist before asking Pablo to review

- [ ] FR, EN and ES pages exist; `hreflang` is reciprocal
- [ ] Every image: name in filename, credit line, alt, figcaption, embedded metadata
- [ ] JSON-LD is valid JSON with the fields above
- [ ] Sitemap includes the new pages and their images; `<lastmod>` updated
- [ ] Every internal link resolves to a file
- [ ] Meta descriptions ≤ 160 characters
- [ ] Every citation verified, or flagged `[SOURCE À VÉRIFIER]`
- [ ] AI-assistance note present in all three versions
- [ ] No placeholders left

## Check the live site after every deploy

GitHub Pages deploys only from `main`, so a pushed branch changes nothing live. After Pablo merges a PR:

1. Wait for the GitHub Pages deployment to finish (the “pages build and deployment” run on `main`).
2. Fetch each changed URL on https://pablocorreaprieto.ch and confirm it returns 200 and shows the change. Also confirm an unknown URL returns the 404 page.
3. Report what you checked. If the site can’t be reached from your environment (the Claude Code cloud environment’s network policy may block the domain), say so explicitly and don’t claim the change is live; ask Pablo to check or to allow the domain.
