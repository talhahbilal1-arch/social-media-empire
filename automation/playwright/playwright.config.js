// Shared Playwright runtime config consumed by the uploader/lister scripts.
// We are not using the @playwright/test runner here — these values are imported
// directly when constructing a persistent browser context.

import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const config = {
  // Persistent auth directory — user logs in once, session survives future runs.
  userDataDir: path.join(__dirname, '.auth'),

  // Headed mode so the user can complete 2FA / captchas manually.
  headless: false,

  // Slow every action slightly so UI has time to react and we can watch it.
  slowMo: 150,

  // Default timeouts (ms).
  navigationTimeout: 60_000,
  actionTimeout: 30_000,

  // Artifacts on failure.
  screenshotOnFailure: true,
  videoOnFailure: true,
  artifactsDir: path.join(__dirname, 'artifacts'),

  // Reports directory for CSV output.
  reportsDir: path.join(__dirname, 'reports'),

  // Viewport big enough for Gumroad's editor.
  viewport: { width: 1440, height: 900 },

  // Launch args — disable automation banners, allow file uploads without prompts.
  launchArgs: [
    '--disable-blink-features=AutomationControlled',
    '--no-default-browser-check',
  ],
};

export default config;
