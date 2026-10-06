// playwright_capture.js — capture HTTP traffic and screenshots for evidence.
// Usage: node scripts/playwright_capture.js <url> [--out <dir>] [--requests <dir>]
// Evidence lands under testing/<root>/<sub>/ by default. Local-only, throttled.

import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const [url, ...rest] = process.argv.slice(2);
if (!url) {
  console.error("usage: node scripts/playwright_capture.js <url> [--out <dir>] [--requests <dir>]");
  process.exit(2);
}

const flag = (name, fallback) => {
  const i = rest.indexOf(`--${name}`);
  return i >= 0 ? rest[i + 1] : fallback;
};

const outDir = path.resolve(flag("out", "testing/evidence"));
const reqDir = path.resolve(flag("requests", outDir));
const slug = new URL(url).hostname.replace(/[^a-z0-9.-]/gi, "_");

await mkdir(outDir, { recursive: true });
await mkdir(reqDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage();

page.on("request", (req) => {
  if (!["document", "xhr", "fetch", "script"].includes(req.resourceType())) return;
  writeFile(
    path.join(reqDir, `${Date.now()}_${req.method()}.txt`),
    `${req.method()} ${req.url()}\n${JSON.stringify(req.headers(), null, 2)}\n`,
  ).catch(() => {});
});

page.on("response", (res) => {
  writeFile(path.join(reqDir, `${Date.now()}_${res.status()}.txt`), `${res.status()} ${res.url()}\n`).catch(() => {});
});

await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
const shot = path.join(outDir, `${slug}_${Date.now()}.png`);
await page.screenshot({ path: shot, fullPage: false });
console.log(`captured: ${shot}`);
await browser.close();