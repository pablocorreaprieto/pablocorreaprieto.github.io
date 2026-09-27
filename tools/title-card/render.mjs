// Renders an article title card (cover) in the site's style.
//
//   node tools/title-card/render.mjs <card.json> [<card.json> ...]
//
// Each JSON file describes one card; see cards/ for the existing ones:
//   out      output path, relative to the repo root (.jpg or .png)
//   kicker   small uppercase line above the title
//   lines    title lines; a trailing "." is drawn in the accent colour
//   tagline  text after the name in the footer (e.g. " · enseignant et recherche en éducation")
//   year     year in the credit line
//   bg       "ground" (default) or "soft"
//
// Output is 1800×945 (the size of the existing covers). Needs Playwright with
// Chromium (preinstalled in the Claude Code cloud environment). Fonts are
// bundled in fonts/ so the output does not depend on the network.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '../..');
const NAME = 'Pablo Correa Prieto';
const DOMAIN = 'pablocorreaprieto.ch';

const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1800, height: 945 } });
for (const file of process.argv.slice(2)) {
  const card = JSON.parse(readFileSync(file, 'utf8'));
  await page.goto(pathToFileURL(resolve(here, 'template.html')).href);
  await page.evaluate(({ card, NAME, DOMAIN }) => {
    const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    document.body.className = card.bg === 'soft' ? 'soft' : '';
    document.getElementById('kicker').textContent = card.kicker || '';
    document.getElementById('title').innerHTML = card.lines
      .map(l => esc(l).replace(/\.$/, '<span class="dot">.</span>')).join('<br>');
    document.getElementById('name').textContent = NAME;
    document.getElementById('tagline').textContent = card.tagline || '';
    document.getElementById('domain').textContent = DOMAIN;
    document.getElementById('credit').textContent = `${NAME} · ${card.year} · CC BY 4.0`;
  }, { card, NAME, DOMAIN });
  await page.evaluate(() => document.fonts.ready);
  const out = resolve(root, card.out);
  await page.screenshot({ path: out, type: out.endsWith('.png') ? 'png' : 'jpeg', quality: out.endsWith('.png') ? undefined : 90 });
  console.log('wrote', card.out);
}
await browser.close();
