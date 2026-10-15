import { defineConfig } from '@playwright/test';
import { resolve } from 'node:path';
const root =
  process.env.CASEWORK_BROWSER_ROOT ??
  resolve(`../.runtime/browser-${Date.now()}`);
process.env.CASEWORK_BROWSER_ROOT = root;
export default defineConfig({
  testDir: './e2e',
  workers: 1,
  fullyParallel: false,
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:5112',
    viewport: { width: 1440, height: 1000 },
    reducedMotion: 'reduce',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: `../.venv/bin/python ../scripts/dev.py run --root "${root}"`,
    url: 'http://127.0.0.1:5112',
    env: { CASEWORK_TEST_DROP_TICKET: '1', CASEWORK_TEST_DROP_ORDER: '1' },
    reuseExistingServer: false,
    timeout: 30000,
    gracefulShutdown: { signal: 'SIGTERM', timeout: 12000 },
  },
});
