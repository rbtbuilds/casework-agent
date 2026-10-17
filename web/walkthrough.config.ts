import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";

const mode = process.env.CASEWORK_RECORDING_MODE;
if (mode !== "model" && mode !== "fixture")
  throw new Error("Set CASEWORK_RECORDING_MODE=model or fixture explicitly.");
const root = resolve(
  process.env.CASEWORK_BROWSER_ROOT ??
    `../.runtime/walkthrough-${mode}-${Date.now()}`,
);
process.env.CASEWORK_BROWSER_ROOT = root;

export default defineConfig({
  testDir: ".",
  testMatch: "walkthrough.spec.ts",
  outputDir: `${root}/playwright`,
  workers: 1,
  retries: 0,
  timeout: 180000,
  use: {
    baseURL: "http://127.0.0.1:5112",
    viewport: { width: 1440, height: 1000 },
    reducedMotion: "reduce",
    locale: "en-GB",
    timezoneId: "UTC",
    video: { mode: "on", size: { width: 1440, height: 1000 } },
    trace: "retain-on-failure",
  },
  webServer: {
    command: `../.venv/bin/python ../scripts/dev.py run --root "${root}"`,
    url: "http://127.0.0.1:5112",
    env: {
      CASEWORK_TEST_DROP_TICKET: mode === "fixture" ? "1" : "0",
      CASEWORK_TEST_DROP_ORDER: mode === "fixture" ? "1" : "0",
    },
    reuseExistingServer: false,
    timeout: 30000,
    gracefulShutdown: { signal: "SIGTERM", timeout: 12000 },
  },
});
