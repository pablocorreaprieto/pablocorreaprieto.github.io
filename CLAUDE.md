# CLAUDE.md

Rules for working on pablocorreaprieto.ch. Structure and the page-editing checklist are in `README.md`; read it first.

## Languages

- **French first.** French is the source language and lives at the root (`/`). Write or change the French page first, then bring English (`/en/`) and Spanish (`/es/`) in line with it.
- **EN and ES stay in sync with FR.** A change to one language is not done until all three pages carry it: visible text, `<title>`, meta description, `og:*` tags, image alt text, JSON-LD, the FR/EN/ES switcher and the `hreflang` links. If a translation can’t be done yet, say so; don’t ship a partial set.
- Content that exists in one language only (e.g. the LinkedIn version of the article, which is French only) stays that way; don’t create translations of it or links to non-existent versions.

## Nothing invented or inflated

- Never add or change facts about Pablo’s research, publications, teaching, qualifications or biography unless he supplied them in the conversation or they already appear on the site. This includes titles, dates, co-authors, venues, institutions, job titles and numbers.
- Don’t upgrade status or wording: “in preparation” is not “submitted” or “published”; a bachelor’s thesis (TFG) is a `Thesis`, not a `ScholarlyArticle`.
- Dates come from the site, from Pablo, or from git history — never estimated.
- Where text is needed and the facts aren’t available, leave a visible placeholder like `[À COMPLÉTER : …]` and list every placeholder in the reply. Never publish a page with placeholders to `main`.
- Structured data (JSON-LD) must describe only what the visible page says.

## Meta descriptions

- `<meta name="description">` is **160 characters or fewer**, in the page’s language. Count before committing.
- Shorten by cutting words or reusing wording already on the page, keeping the meaning; don’t add claims to fill space.
- Keep `og:description` identical to the meta description unless the page deliberately uses a different one (the home pages do).

## Git workflow

- **Never push to `main`.** Work on a branch and open a pull request; Pablo reviews and merges.
- Keep PRs focused, and describe every change and anything left open in the PR body.
- Before opening a PR: every internal link and sitemap URL resolves to a file, all JSON-LD parses, and `<lastmod>` in `sitemap.xml` is updated for every page you changed.

## Check the live site after every deploy

GitHub Pages deploys only from `main`, so a push to a branch changes nothing live. After a PR is merged:

1. Wait for the GitHub Pages deployment to finish (the “pages build and deployment” run on `main`).
2. Fetch each changed URL on https://pablocorreaprieto.ch and confirm it returns 200 and shows the change (e.g. the new text or meta description). Also confirm an unknown URL returns the 404 page.
3. Report what you checked. If the site can’t be reached from your environment (the Claude Code cloud environment’s network policy may block the domain), say so explicitly and don’t claim the change is live; ask Pablo to check or to allow the domain.
