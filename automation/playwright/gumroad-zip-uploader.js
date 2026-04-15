// Gumroad ZIP uploader
// --------------------
// Gumroad's public API does not support file uploads, so this script drives
// the web UI with Playwright. It uses a persistent browser context so the user
// only logs in once; subsequent runs reuse the session cookies stored under
// ./.auth/.
//
// Usage:
//   node gumroad-zip-uploader.js           # real run
//   node gumroad-zip-uploader.js --dry-run # log actions only, no submits
//
// The script reads gumroad-manifest.json for the list of products, iterates
// each one, and emits a CSV report under ./reports/.
// Per-product errors are caught so one bad product does not abort the batch.

import { chromium } from 'playwright';
import { promises as fs } from 'node:fs';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import config from './playwright.config.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes('--dry-run');

const MANIFEST_PATH = path.join(__dirname, 'gumroad-manifest.json');
const REPORTS_DIR = config.reportsDir;

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

function logLine(prefix, msg) {
  const stamp = new Date().toISOString();
  console.log(`[${stamp}] [${prefix}] ${msg}`);
}

function csvEscape(value) {
  const s = String(value ?? '');
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeReport(rows) {
  await ensureDir(REPORTS_DIR);
  const out = path.join(REPORTS_DIR, `gumroad-uploads-${timestamp()}.csv`);
  const header = ['slug', 'title', 'zip', 'status', 'detail', 'durationMs'];
  const lines = [header.join(',')];
  for (const r of rows) {
    lines.push(header.map(h => csvEscape(r[h])).join(','));
  }
  await fs.writeFile(out, lines.join('\n') + '\n', 'utf8');
  return out;
}

// Attempt to detect whether the product already has a file attached by looking
// for a filename badge in the content section. We search broadly because
// Gumroad's markup drifts over time.
async function productAlreadyHasFile(page) {
  const markers = [
    'Replace file',
    'Download file',
    '.zip',
  ];
  for (const m of markers) {
    const loc = page.getByText(m, { exact: false }).first();
    if (await loc.count().catch(() => 0)) {
      if (await loc.isVisible().catch(() => false)) return true;
    }
  }
  return false;
}

async function uploadForProduct(context, product) {
  const startedAt = Date.now();
  const row = {
    slug: product.slug,
    title: product.title,
    zip: product.zip,
    status: 'unknown',
    detail: '',
    durationMs: 0,
  };

  const zipPath = path.resolve(__dirname, product.zip);
  if (!existsSync(zipPath)) {
    row.status = 'missing_zip';
    row.detail = `Zip not found at ${zipPath}`;
    row.durationMs = Date.now() - startedAt;
    logLine(product.slug, `SKIP — ${row.detail}`);
    return row;
  }

  const page = await context.newPage();
  page.setDefaultTimeout(config.actionTimeout);
  page.setDefaultNavigationTimeout(config.navigationTimeout);

  try {
    const editUrl = `https://gumroad.com/products/${product.slug}/edit`;
    logLine(product.slug, `Navigating to ${editUrl}`);
    await page.goto(editUrl, { waitUntil: 'domcontentloaded' });

    // If the session is not authenticated Gumroad redirects to /login.
    if (/\/login/i.test(page.url())) {
      row.status = 'needs_login';
      row.detail = 'Redirected to /login — run once headed and log in.';
      logLine(product.slug, row.detail);
      return row;
    }

    // Open the Content tab. Gumroad uses a left-rail tab list.
    const contentTab = page.getByRole('tab', { name: /content/i }).first();
    if (await contentTab.count()) {
      await contentTab.click().catch(() => {});
    } else {
      // Fallback: link text.
      await page.getByRole('link', { name: /content/i }).first().click().catch(() => {});
    }
    await page.waitForLoadState('networkidle').catch(() => {});

    if (await productAlreadyHasFile(page)) {
      row.status = 'skipped_has_file';
      row.detail = 'File already attached, leaving as-is.';
      logLine(product.slug, row.detail);
      return row;
    }

    if (DRY_RUN) {
      row.status = 'dry_run';
      row.detail = `Would upload ${zipPath}`;
      logLine(product.slug, `DRY RUN — ${row.detail}`);
      return row;
    }

    // Find the file input. Gumroad hides it behind a styled drop-zone.
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.waitFor({ state: 'attached' });
    logLine(product.slug, `Uploading ${path.basename(zipPath)}`);
    await fileInput.setInputFiles(zipPath);

    // Wait for the upload to finish — look for the filename badge or
    // the disappearance of any progress bar. We poll up to 5 minutes.
    const uploadDeadline = Date.now() + 5 * 60_000;
    while (Date.now() < uploadDeadline) {
      const badge = page.getByText(path.basename(zipPath), { exact: false }).first();
      if (await badge.count().catch(() => 0)) break;
      await page.waitForTimeout(1500);
    }

    // Save — Gumroad shows a Save button at the top-right.
    const saveBtn = page.getByRole('button', { name: /^save( changes)?$/i }).first();
    await saveBtn.click({ timeout: 15_000 });

    // Confirmation toast.
    await page.getByText(/saved|changes saved/i).first().waitFor({ timeout: 20_000 }).catch(() => {});

    row.status = 'uploaded';
    row.detail = `Attached ${path.basename(zipPath)}`;
    logLine(product.slug, `OK — ${row.detail}`);
  } catch (err) {
    row.status = 'error';
    row.detail = err?.message?.slice(0, 500) ?? String(err);
    logLine(product.slug, `ERROR — ${row.detail}`);
    const shotDir = config.artifactsDir;
    await ensureDir(shotDir);
    const shotPath = path.join(shotDir, `gumroad-${product.slug}-${timestamp()}.png`);
    await page.screenshot({ path: shotPath, fullPage: true }).catch(() => {});
  } finally {
    row.durationMs = Date.now() - startedAt;
    await page.close().catch(() => {});
  }
  return row;
}

async function main() {
  const manifest = JSON.parse(await fs.readFile(MANIFEST_PATH, 'utf8'));
  logLine('boot', `Loaded ${manifest.products.length} products (dryRun=${DRY_RUN})`);

  await ensureDir(config.userDataDir);
  const context = await chromium.launchPersistentContext(config.userDataDir, {
    headless: config.headless,
    slowMo: config.slowMo,
    viewport: config.viewport,
    args: config.launchArgs,
    acceptDownloads: true,
  });

  const rows = [];
  try {
    for (const product of manifest.products) {
      const row = await uploadForProduct(context, product);
      rows.push(row);
    }
  } finally {
    const report = await writeReport(rows);
    logLine('report', `Wrote ${report}`);
    await context.close().catch(() => {});
  }

  const summary = rows.reduce((acc, r) => {
    acc[r.status] = (acc[r.status] ?? 0) + 1;
    return acc;
  }, {});
  logLine('done', `Summary: ${JSON.stringify(summary)}`);
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
