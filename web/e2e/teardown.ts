import { execFileSync } from 'node:child_process';
export default function teardown() { const root = process.env.CASEWORK_BROWSER_ROOT; if (root) execFileSync('../.venv/bin/python', ['../scripts/dev.py','stop','--root',root], {stdio:'inherit'}); }
