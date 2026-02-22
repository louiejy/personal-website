import puppeteer from 'puppeteer';
import { mkdir } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { existsSync, readdirSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const url = process.argv[2] || 'http://localhost:3000';
const label = process.argv[3] || '';

const screenshotDir = join(__dirname, 'temporary screenshots');
await mkdir(screenshotDir, { recursive: true });

// Find next available number
let n = 1;
if (existsSync(screenshotDir)) {
  const files = readdirSync(screenshotDir);
  const nums = files
    .map(f => parseInt(f.match(/^screenshot-(\d+)/)?.[1]))
    .filter(Boolean);
  if (nums.length) n = Math.max(...nums) + 1;
}

const filename = label ? `screenshot-${n}-${label}.png` : `screenshot-${n}.png`;
const outputPath = join(screenshotDir, filename);

const browser = await puppeteer.launch({ headless: 'new' });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
await page.goto(url, { waitUntil: 'networkidle0' });

// Force all scroll-reveal elements visible for screenshot
await page.evaluate(() => {
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
});
// Wait for transitions + hero animations to finish
await new Promise(r => setTimeout(r, 900));

await page.screenshot({ path: outputPath, fullPage: true });
await browser.close();

console.log(`Screenshot saved to: ${outputPath}`);
