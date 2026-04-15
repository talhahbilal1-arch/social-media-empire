#!/usr/bin/env node
/**
 * follow-up-tracker.js — Reads reports/applications.csv and emits a markdown
 * report of pending affiliate applications. Flags anything > 14 days old for
 * manual follow-up (most programs approve within 7-14 days).
 *
 * Usage:
 *   node follow-up-tracker.js
 *   node follow-up-tracker.js --out reports/follow-up.md
 *   node follow-up-tracker.js --stale 14
 */

import { readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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

/** Minimal CSV parser that handles quoted fields + escaped quotes. */
function parseCsv(text) {
  const rows = [];
  let field = '';
  let row = [];
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else { inQuotes = false; }
      } else {
        field += c;
      }
    } else {
      if (c === '"') {
        inQuotes = true;
      } else if (c === ',') {
        row.push(field); field = '';
      } else if (c === '\n') {
        row.push(field); field = '';
        rows.push(row); row = [];
      } else if (c === '\r') {
        // skip
      } else {
        field += c;
      }
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function toRecords(rows) {
  if (rows.length === 0) return [];
  const header = rows[0];
  const records = [];
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    if (r.length === 1 && r[0] === '') continue;
    const obj = {};
    header.forEach((h, idx) => { obj[h] = r[idx] ?? ''; });
    records.push(obj);
  }
  return records;
}

function daysSince(iso) {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return null;
  const ms = Date.now() - then;
  return Math.floor(ms / (1000 * 60 * 60 * 24));
}

function buildReport(records, staleDays) {
  const now = new Date().toISOString();
  const lines = [];
  lines.push('# Affiliate Application Follow-Up Report');
  lines.push('');
  lines.push(`_Generated: ${now}_`);
  lines.push(`_Stale threshold: ${staleDays} days_`);
  lines.push('');

  if (records.length === 0) {
    lines.push('No applications logged yet. Run `node apply.js --program <slug>` to start.');
    return lines.join('\n') + '\n';
  }

  const enriched = records.map((r) => {
    const age = daysSince(r.submitted_at);
    return { ...r, _age: age ?? -1 };
  });

  const pending = enriched.filter((r) => r.status === 'submitted' || r.status === 'pending_user_action');
  const stale = pending.filter((r) => r._age >= staleDays);
  const fresh = pending.filter((r) => r._age < staleDays);
  const errors = enriched.filter((r) => r.status === 'error');

  lines.push('## Summary');
  lines.push('');
  lines.push(`- Total applications logged: **${enriched.length}**`);
  lines.push(`- Pending (awaiting approval): **${pending.length}**`);
  lines.push(`- Stale (> ${staleDays} days, needs follow-up): **${stale.length}**`);
  lines.push(`- Errors: **${errors.length}**`);
  lines.push('');

  const renderTable = (rs) => {
    const out = [];
    out.push('| Program | Slug | Submitted | Days Old | Status | Notes |');
    out.push('|---------|------|-----------|----------|--------|-------|');
    for (const r of rs) {
      const notes = (r.notes || '').replace(/\|/g, '\\|').slice(0, 120);
      out.push(`| ${r.program_name} | ${r.program_slug} | ${r.submitted_at} | ${r._age} | ${r.status} | ${notes} |`);
    }
    return out.join('\n');
  };

  if (stale.length) {
    lines.push(`## Needs Manual Follow-Up (> ${staleDays} days)`);
    lines.push('');
    lines.push('These applications have been pending longer than typical approval windows. Email the program manager or check your application status directly.');
    lines.push('');
    lines.push(renderTable(stale.sort((a, b) => b._age - a._age)));
    lines.push('');
  }

  if (fresh.length) {
    lines.push('## Pending (within normal approval window)');
    lines.push('');
    lines.push(renderTable(fresh.sort((a, b) => b._age - a._age)));
    lines.push('');
  }

  if (errors.length) {
    lines.push('## Errors');
    lines.push('');
    lines.push(renderTable(errors.sort((a, b) => b._age - a._age)));
    lines.push('');
  }

  const approved = enriched.filter((r) => r.status === 'approved');
  if (approved.length) {
    lines.push('## Approved');
    lines.push('');
    lines.push(renderTable(approved));
    lines.push('');
  }

  return lines.join('\n') + '\n';
}

async function main() {
  const args = parseArgs(process.argv);
  const staleDays = Number(args.stale ?? 14);
  const csvPath = resolve(__dirname, 'reports', 'applications.csv');

  if (!existsSync(csvPath)) {
    console.log(`# Affiliate Application Follow-Up Report`);
    console.log('');
    console.log(`No CSV found at ${csvPath}. Run apply.js first.`);
    return;
  }

  const raw = await readFile(csvPath, 'utf8');
  const rows = parseCsv(raw);
  const records = toRecords(rows);
  const report = buildReport(records, staleDays);

  if (args.out) {
    const outPath = resolve(args.out);
    await writeFile(outPath, report, 'utf8');
    console.log(`Report written to ${outPath}`);
  } else {
    process.stdout.write(report);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
