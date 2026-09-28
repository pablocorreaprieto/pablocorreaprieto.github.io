// Renders figure SVGs (from figures.py) to PNG at 1800×945, next to the site pages.
//
//   node tools/figures/render.mjs tools/figures/svg/*.svg
//
// Output: <repo root>/<same basename>.png. Warns when a text element is wider
// than its data-maxw (text overflow), so check the warnings before using a PNG.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '../..');
const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1800, height: 945 } });
let warnings = 0;
for (const file of process.argv.slice(2)) {
  await page.goto(pathToFileURL(resolve(file)).href);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(150);
  const over = await page.evaluate(() => [...document.querySelectorAll('text[data-maxw]')]
    .map(el => ({ w: el.getBBox().width, max: +el.dataset.maxw, s: el.textContent.slice(0, 60) }))
    .filter(o => o.w > o.max + 0.5));
  for (const o of over) { warnings++; console.log(`  OVERFLOW ${basename(file)}: ${Math.round(o.w)} > ${o.max} "${o.s}"`); }
  const out = resolve(root, basename(file).replace(/\.svg$/, '.png'));
  await page.screenshot({ path: out, type: 'png' });
  console.log('wrote', basename(out));
}
await browser.close();
if (warnings) process.exitCode = 1;
