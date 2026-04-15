#!/usr/bin/env node
/**
 * apply.js — Assisted affiliate-program signup.
 *
 * Usage:
 *   node apply.js --program <slug>
 *   node apply.js --program semrush
 *
 * Opens a persistent Chromium context, navigates to the program's apply URL,
 * best-effort pre-fills the form using heuristic selectors, pauses for CAPTCHA
 * and final human review, then captures a screenshot + CSV log entry.
 *
 * NEVER auto-submits. Always stops before Submit for human review.
 */

import { chromium } from 'playwright';
import { readFile, mkdir, appendFile, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import readline from 'node:readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// -------- CLI parsing --------
function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

function prompt(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolveP) => {
    rl.question(question, (answer) => {
      rl.close();
      resolveP(answer);
    });
  });
}

async function waitForEnter(message) {
  console.log('');
  console.log('=============================================================');
  console.log(message);
  console.log('=============================================================');
  await prompt('>>> Press ENTER when ready to continue... ');
}

// -------- Resilient field-fill helpers --------

/**
 * Try a list of selectors in order; fill the first visible, editable match.
 * Returns true if something was filled.
 */
async function tryFill(page, selectors, value) {
  if (value === undefined || value === null || value === '') return false;
  for (const sel of selectors) {
    try {
      const locators = page.locator(sel);
      const count = await locators.count();
      for (let i = 0; i < count; i++) {
        const el = locators.nth(i);
        if (await el.isVisible().catch(() => false)) {
          const editable = await el.isEditable().catch(() => false);
          if (editable) {
            await el.fill(String(value), { timeout: 2000 }).catch(() => {});
            const val = await el.inputValue().catch(() => '');
            if (val === String(value)) return true;
          }
        }
      }
    } catch (_) { /* keep trying */ }
  }
  return false;
}

async function trySelect(page, selectors, value) {
  if (!value) return false;
  for (const sel of selectors) {
    try {
      const el = page.locator(sel).first();
      if (await el.isVisible().catch(() => false)) {
        await el.selectOption({ label: value }).catch(async () => {
          await el.selectOption(value).catch(() => {});
        });
        return true;
      }
    } catch (_) {}
  }
  return false;
}

/**
 * Heuristic-based form filler. Tries multiple selector strategies per field.
 */
async function fillForm(page, profile) {
  const filled = [];
  const record = (label, ok) => { if (ok) filled.push(label); };

  // Email
  record('email', await tryFill(page, [
    'input[type="email"]',
    'input[name*="email" i]',
    'input[id*="email" i]',
    'input[placeholder*="email" i]',
    'input[aria-label*="email" i]',
  ], profile.email));

  // First / last / full name
  record('first_name', await tryFill(page, [
    'input[name*="first" i]',
    'input[id*="first" i]',
    'input[placeholder*="first name" i]',
    'input[aria-label*="first name" i]',
  ], profile.first_name));

  record('last_name', await tryFill(page, [
    'input[name*="last" i]',
    'input[id*="last" i]',
    'input[placeholder*="last name" i]',
    'input[aria-label*="last name" i]',
  ], profile.last_name));

  record('full_name', await tryFill(page, [
    'input[name="name"]',
    'input[name*="fullname" i]',
    'input[name*="full_name" i]',
    'input[name*="full-name" i]',
    'input[id*="fullname" i]',
    'input[placeholder*="full name" i]',
    'input[placeholder="Name"]',
  ], profile.full_name));

  // Phone
  record('phone', await tryFill(page, [
    'input[type="tel"]',
    'input[name*="phone" i]',
    'input[id*="phone" i]',
    'input[placeholder*="phone" i]',
  ], profile.phone));

  // Website / URL
  record('website', await tryFill(page, [
    'input[type="url"]',
    'input[name*="website" i]',
    'input[name*="url" i]',
    'input[name*="site" i]',
    'input[id*="website" i]',
    'input[placeholder*="website" i]',
    'input[placeholder*="URL" i]',
    'input[placeholder*="your site" i]',
  ], profile.website));

  // Promotion / audience description (textarea)
  record('promotion_description', await tryFill(page, [
    'textarea[name*="promot" i]',
    'textarea[name*="describe" i]',
    'textarea[name*="how" i]',
    'textarea[placeholder*="promot" i]',
    'textarea[placeholder*="describe" i]',
    'textarea[placeholder*="audience" i]',
    'textarea',
  ], profile.promotion_description || profile.audience_description));

  // PayPal
  record('paypal_email', await tryFill(page, [
    'input[name*="paypal" i]',
    'input[id*="paypal" i]',
    'input[placeholder*="paypal" i]',
  ], profile.paypal_email));

  // Tax ID / SSN
  record('tax_id', await tryFill(page, [
    'input[name*="tax" i]',
    'input[name*="ssn" i]',
    'input[name*="ein" i]',
    'input[id*="tax" i]',
    'input[placeholder*="tax" i]',
  ], profile.tax_id));

  // Pageviews / audience size
  record('monthly_pageviews', await tryFill(page, [
    'input[name*="pageview" i]',
    'input[name*="traffic" i]',
    'input[name*="visitors" i]',
    'input[placeholder*="pageview" i]',
    'input[placeholder*="traffic" i]',
  ], profile.monthly_pageviews));

  record('audience_size', await tryFill(page, [
    'input[name*="audience" i]',
    'input[name*="followers" i]',
    'input[placeholder*="audience size" i]',
  ], profile.audience_size));

  // Address
  const addr = profile.address || {};
  record('address_line1', await tryFill(page, [
    'input[name*="address1" i]',
    'input[name*="street" i]',
    'input[name*="addr1" i]',
    'input[name="address"]',
    'input[placeholder*="street" i]',
    'input[placeholder*="address line 1" i]',
  ], addr.line1));
  record('address_line2', await tryFill(page, [
    'input[name*="address2" i]',
    'input[name*="addr2" i]',
    'input[placeholder*="address line 2" i]',
    'input[placeholder*="apt" i]',
  ], addr.line2));
  record('city', await tryFill(page, [
    'input[name*="city" i]',
    'input[id*="city" i]',
    'input[placeholder*="city" i]',
  ], addr.city));
  record('state', await tryFill(page, [
    'input[name*="state" i]',
    'input[name*="region" i]',
    'input[placeholder*="state" i]',
  ], addr.state));
  record('postal_code', await tryFill(page, [
    'input[name*="zip" i]',
    'input[name*="postal" i]',
    'input[id*="zip" i]',
    'input[placeholder*="zip" i]',
    'input[placeholder*="postal" i]',
  ], addr.postal_code));

  // Country (often a select)
  const country = addr.country || profile.country;
  if (country) {
    const ok = await trySelect(page, [
      'select[name*="country" i]',
      'select[id*="country" i]',
    ], country === 'US' ? 'United States' : country);
    record('country', ok);
  }

  // Business name
  record('business_name', await tryFill(page, [
    'input[name*="company" i]',
    'input[name*="business" i]',
    'input[placeholder*="company" i]',
    'input[placeholder*="business name" i]',
  ], profile.business_name));

  // Social handles
  const soc = profile.social_handles || {};
  for (const [platform, handle] of Object.entries(soc)) {
    if (!handle) continue;
    record(`social_${platform}`, await tryFill(page, [
      `input[name*="${platform}" i]`,
      `input[placeholder*="${platform}" i]`,
      `input[aria-label*="${platform}" i]`,
    ], handle));
  }

  return filled;
}

// -------- CSV logging --------

async function ensureDir(p) {
  if (!existsSync(p)) await mkdir(p, { recursive: true });
}

async function appendCsvRow(csvPath, row) {
  const header = 'program_slug,program_name,submitted_at,screenshot_path,status,notes\n';
  const exists = existsSync(csvPath);
  if (!exists) await appendFile(csvPath, header, 'utf8');
  const esc = (v) => {
    const s = String(v ?? '');
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
      return `"${s.replace(/"/g, '""')}"`;
    }
    return s;
  };
  const line = [
    row.program_slug,
    row.program_name,
    row.submitted_at,
    row.screenshot_path,
    row.status,
    row.notes,
  ].map(esc).join(',') + '\n';
  await appendFile(csvPath, line, 'utf8');
}

// -------- Main --------

async function main() {
  const args = parseArgs(process.argv);
  const slug = args.program;
  if (!slug) {
    console.error('Usage: node apply.js --program <slug>');
    console.error('Available slugs: semrush, hostinger, ahrefs, frase, clickbank');
    process.exit(1);
  }

  const programsPath = join(__dirname, 'programs.json');
  const profilePath = join(__dirname, 'applicant-profile.json');

  const programs = JSON.parse(await readFile(programsPath, 'utf8'));
  const profile = JSON.parse(await readFile(profilePath, 'utf8'));

  const program = programs[slug];
  if (!program) {
    console.error(`Unknown program slug "${slug}". Available: ${Object.keys(programs).join(', ')}`);
    process.exit(1);
  }

  // Warn if profile still has placeholders
  if (profile.email === 'YOUR_EMAIL' || profile.full_name === 'YOUR_NAME') {
    console.log('');
    console.log('!!! WARNING: applicant-profile.json still contains placeholder values.');
    console.log('!!! Edit that file with your real info before continuing, or the form');
    console.log('!!! will be pre-filled with placeholder strings.');
    const answer = await prompt('Continue anyway? (y/N) ');
    if (!answer.toLowerCase().startsWith('y')) {
      console.log('Aborted.');
      process.exit(0);
    }
  }

  const authDir = resolve(__dirname, '.auth', slug);
  const reportsDir = resolve(__dirname, 'reports');
  await ensureDir(authDir);
  await ensureDir(reportsDir);

  console.log(`\n>>> Launching browser for: ${program.name}`);
  console.log(`>>> Apply URL: ${program.apply_url}`);
  console.log(`>>> Persistent auth: ${authDir}`);

  const context = await chromium.launchPersistentContext(authDir, {
    headless: false,
    viewport: { width: 1280, height: 900 },
    args: ['--disable-blink-features=AutomationControlled'],
  });

  const page = context.pages()[0] || await context.newPage();

  let status = 'error';
  let notes = '';
  let screenshotPath = '';
  const submittedAt = new Date().toISOString();

  try {
    await page.goto(program.apply_url, { waitUntil: 'domcontentloaded', timeout: 60000 });

    await waitForEnter(
      `1/3  NAVIGATE\n\nBrowser is at: ${program.apply_url}\n\n` +
      `If this page is just marketing, CLICK THE "APPLY" / "SIGN UP" / "JOIN" button\n` +
      `to reach the actual signup form. If the program requires an account first,\n` +
      `log in or create one now. Press ENTER when the signup form is visible.`
    );

    console.log('\n>>> Attempting heuristic form fill...');
    const filled = await fillForm(page, profile);
    if (filled.length === 0) {
      console.log('    No fields matched. You may be on a non-form page, or the form uses');
      console.log('    custom components. Fill the form manually.');
      notes = 'no fields auto-matched';
    } else {
      console.log(`    Pre-filled ${filled.length} field(s): ${filled.join(', ')}`);
      notes = `auto-filled: ${filled.join('|')}`;
    }

    await waitForEnter(
      `2/3  REVIEW + CAPTCHA\n\n` +
      `* Check every field for accuracy.\n` +
      `* Fix anything the script missed (dropdowns, checkboxes, file uploads).\n` +
      `* Solve any CAPTCHA.\n` +
      `* DO NOT click Submit yet — screenshot happens first.\n\n` +
      `Press ENTER when the form is complete and CAPTCHA is solved.`
    );

    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    screenshotPath = join(reportsDir, `${slug}-${stamp}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`>>> Screenshot saved: ${screenshotPath}`);

    await waitForEnter(
      `3/3  SUBMIT\n\n` +
      `You're cleared to click the SUBMIT button manually in the browser.\n` +
      `Wait for the confirmation page to load, then press ENTER here to log the result.`
    );

    const outcome = (await prompt('Status? [s=submitted, p=pending_user_action, e=error]: ')).trim().toLowerCase();
    status = outcome === 's' ? 'submitted'
      : outcome === 'p' ? 'pending_user_action'
      : outcome === 'e' ? 'error'
      : 'submitted';

    const extraNotes = (await prompt('Any notes (optional, single line): ')).trim();
    if (extraNotes) notes = notes ? `${notes} | ${extraNotes}` : extraNotes;
  } catch (err) {
    status = 'error';
    notes = `exception: ${err.message}`;
    console.error('!!! Error during apply:', err);
  } finally {
    const csvPath = join(reportsDir, 'applications.csv');
    await appendCsvRow(csvPath, {
      program_slug: slug,
      program_name: program.name,
      submitted_at: submittedAt,
      screenshot_path: screenshotPath,
      status,
      notes,
    });
    console.log(`\n>>> Logged to ${csvPath} (status=${status})`);
    await context.close();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
