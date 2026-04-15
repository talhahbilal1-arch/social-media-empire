// PromptBase lister
// -----------------
// Drives promptbase.com/sell in a persistent Chromium context to submit each
// prompt pack as a draft listing. One login per machine; sessions persist in
// ./.auth/.
//
// Usage:
//   node promptbase-lister.js           # real run
//   node promptbase-lister.js --dry-run # log only, do not submit
//
// Per-prompt errors are isolated so one bad listing does not abort the batch.

import { chromium } from 'playwright';
import { promises as fs } from 'node:fs';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import config from './playwright.config.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes('--dry-run');

const MANIFEST_PATH = path.join(__dirname, 'promptbase-manifest.json');
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots');
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
  const out = path.join(REPORTS_DIR, `promptbase-listings-${timestamp()}.csv`);
  const header = ['slug', 'title', 'price', 'status', 'detail', 'durationMs'];
  const lines = [header.join(',')];
  for (const r of rows) {
    lines.push(header.map(h => csvEscape(r[h])).join(','));
  }
  await fs.writeFile(out, lines.join('\n') + '\n', 'utf8');
  return out;
}

// Try a sequence of locator strategies to find a form field. PromptBase's UI
// labels have changed multiple times; we prefer accessibility roles first.
async function fillByLabelOrPlaceholder(page, labelRegex, value) {
  const tries = [
    () => page.getByLabel(labelRegex).first(),
    () => page.getByPlaceholder(labelRegex).first(),
    () => page.getByRole('textbox', { name: labelRegex }).first(),
  ];
  for (const t of tries) {
    const loc = t();
    if (await loc.count().catch(() => 0)) {
      await loc.fill(String(value));
      return true;
    }
  }
  return false;
}

async function selectByLabel(page, labelRegex, value) {
  const loc = page.getByLabel(labelRegex).first();
  if (await loc.count().catch(() => 0)) {
    await loc.selectOption({ label: String(value) }).catch(async () => {
      await loc.selectOption(String(value)).catch(() => {});
    });
    return true;
  }
  return false;
}

async function listPrompt(context, entry, defaults) {
  const startedAt = Date.now();
  const row = {
    slug: entry.slug,
    title: entry.title,
    price: entry.price ?? defaults.price,
    status: 'unknown',
    detail: '',
    durationMs: 0,
  };

  const page = await context.newPage();
  page.setDefaultTimeout(config.actionTimeout);
  page.setDefaultNavigationTimeout(config.navigationTimeout);

  try {
    logLine(entry.slug, 'Navigating to https://promptbase.com/sell');
    await page.goto('https://promptbase.com/sell', { waitUntil: 'domcontentloaded' });

    if (/\/login|\/signin/i.test(page.url())) {
      row.status = 'needs_login';
      row.detail = 'Redirected to login — run once headed and log in.';
      logLine(entry.slug, row.detail);
      return row;
    }

    // Fill the common fields. We probe each label with a regex so small UI
    // copy changes do not break us.
    await fillByLabelOrPlaceholder(page, /title/i, entry.title);
    await fillByLabelOrPlaceholder(page, /description|about/i, entry.description);
    await fillByLabelOrPlaceholder(page, /example( prompt)?|sample/i, entry.example_prompt);
    await fillByLabelOrPlaceholder(page, /price|usd/i, String(entry.price ?? defaults.price));

    await selectByLabel(page, /category/i, entry.category ?? defaults.category);
    await selectByLabel(page, /model|engine/i, entry.model ?? defaults.model);

    // Optional screenshot upload — only if a file exists for this slug.
    const shot = path.join(SCREENSHOT_DIR, `${entry.slug}.png`);
    if (existsSync(shot)) {
      const fileInput = page.locator('input[type="file"]').first();
      if (await fileInput.count().catch(() => 0)) {
        await fileInput.setInputFiles(shot).catch(() => {});
        logLine(entry.slug, `Attached screenshot ${shot}`);
      }
    }

    if (DRY_RUN) {
      row.status = 'dry_run';
      row.detail = 'Form filled, submit skipped (dry-run).';
      logLine(entry.slug, `DRY RUN — ${row.detail}`);
      return row;
    }

    // Save as draft. PromptBase typically offers "Save draft" next to "Submit".
    const draftBtn = page
      .getByRole('button', { name: /save (as )?draft|save draft/i })
      .first();
    if (await draftBtn.count().catch(() => 0)) {
      await draftBtn.click();
    } else {
      // Fallback: submit button (may publish for review; user can still
      // unpublish manually).
      await page.getByRole('button', { name: /submit|publish/i }).first().click();
    }

    await page
      .getByText(/draft saved|saved|submitted|under review/i)
      .first()
      .waitFor({ timeout: 20_000 })
      .catch(() => {});

    row.status = 'submitted';
    row.detail = 'Draft saved (or submitted for review).';
    logLine(entry.slug, `OK — ${row.detail}`);
  } catch (err) {
    row.status = 'error';
    row.detail = err?.message?.slice(0, 500) ?? String(err);
    logLine(entry.slug, `ERROR — ${row.detail}`);
    const shotDir = config.artifactsDir;
    await ensureDir(shotDir);
    const shotPath = path.join(shotDir, `promptbase-${entry.slug}-${timestamp()}.png`);
    await page.screenshot({ path: shotPath, fullPage: true }).catch(() => {});
  } finally {
    row.durationMs = Date.now() - startedAt;
    await page.close().catch(() => {});
  }
  return row;
}

async function main() {
  const manifest = JSON.parse(await fs.readFile(MANIFEST_PATH, 'utf8'));
  logLine('boot', `Loaded ${manifest.prompts.length} prompts (dryRun=${DRY_RUN})`);

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
    for (const entry of manifest.prompts) {
      const row = await listPrompt(context, entry, manifest.defaults);
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
