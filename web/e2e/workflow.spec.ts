import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { execFileSync } from 'node:child_process';
import { parseCase } from '../src/api/schema';

test('actual service approval, replay, recovery and responsive accessible states', async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/');
  await page
    .getByRole('button', { name: 'Open delayed delivery example' })
    .click();
  await expect(
    page.getByRole('button', { name: 'Approve fictional action' }),
  ).toBeVisible();
  await expect(
    page.getByText('Fixture workflow', { exact: true }).last(),
  ).toBeVisible();
  const cases: unknown = await (
    await request.get('http://127.0.0.1:8112/v1/cases')
  ).json();
  if (!Array.isArray(cases) || !cases[0]) throw new Error('No case created.');
  const before = parseCase(cases[0]);
  if (!before.proposal) throw new Error('Proposal missing.');
  await page.screenshot({
    path: '../.runtime/evidence/desktop-light.png',
    fullPage: true,
  });
  const light = await new AxeBuilder({ page }).analyze();
  expect(light.violations).toEqual([]);
  const approvalResponse = page.waitForResponse(
    (r) => r.url().endsWith('/decisions') && r.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Approve fictional action' }).focus();
  await page.keyboard.press('Enter');
  await expect(
    page.getByText('Ticket confirmed', { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText('Order annotation confirmed', { exact: true }),
  ).toBeVisible();
  const firstApproval = await approvalResponse;
  const key = firstApproval.request().headers()['idempotency-key'];
  if (!key) throw new Error('Approval key missing.');
  const original: unknown = firstApproval.request().postDataJSON();
  const replay = await request.post(
    `http://127.0.0.1:8112/v1/cases/${before.id}/decisions`,
    { data: original, headers: { 'Idempotency-Key': key } },
  );
  expect(await replay.json()).toEqual(await firstApproval.json());
  const changed = await request.post(
    `http://127.0.0.1:8112/v1/cases/${before.id}/decisions`,
    {
      data: {
        proposal_id: before.proposal.id,
        proposal_hash: '0'.repeat(64),
        expected_case_version: before.version,
        decision: 'approve',
      },
      headers: { 'Idempotency-Key': key },
    },
  );
  expect(changed.status()).toBe(409);
  const counts = execFileSync(
    '../.venv/bin/python',
    [
      '-c',
      "import sqlite3,json;from pathlib import Path;import os;r=Path(os.environ['CASEWORK_BROWSER_ROOT']);print(json.dumps([sqlite3.connect(r/'tickets.sqlite3').execute('select count(*) from tickets').fetchone()[0],sqlite3.connect(r/'orders.sqlite3').execute('select count(*) from annotations').fetchone()[0]]))",
    ],
    { encoding: 'utf8' },
  );
  expect(JSON.parse(counts)).toEqual([1, 1]);
  await page.getByRole('combobox', { name: 'Appearance' }).selectOption('dark');
  await page.screenshot({
    path: '../.runtime/evidence/desktop-dark.png',
    fullPage: true,
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.setViewportSize({ width: 375, height: 812 });
  await page.screenshot({
    path: '../.runtime/evidence/mobile-dark.png',
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page
    .getByRole('combobox', { name: 'Appearance' })
    .selectOption('light');
  await page.screenshot({
    path: '../.runtime/evidence/mobile-light.png',
    fullPage: true,
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  expect(errors).toEqual([]);
});

test('expired proposal becomes stale and can be renewed through the browser', async ({
  page,
}) => {
  await page.goto('/');
  await page
    .getByRole('button', { name: 'Open delayed delivery example' })
    .click();
  await expect(
    page.getByRole('button', { name: 'Approve fictional action' }),
  ).toBeVisible();
  execFileSync('../.venv/bin/python', [
    '-c',
    "import os;from pathlib import Path;from datetime import datetime,timedelta;p=Path(os.environ['CASEWORK_BROWSER_ROOT'])/'clock.txt';v=datetime.fromisoformat(p.read_text())+timedelta(seconds=901);t=p.with_suffix('.next');t.write_text(v.isoformat());t.replace(p)",
  ]);
  await expect(page.getByRole('status')).toHaveText('stale');
  await expect(
    page.getByRole('button', { name: 'Approve fictional action' }),
  ).toHaveCount(0);
  await page.getByRole('button', { name: 'Gather a new proposal' }).click();
  await expect(
    page.getByRole('button', { name: 'Approve fictional action' }),
  ).toBeVisible();
  await expect(page.getByText('Version 2', { exact: true })).toBeVisible();
});

test('lost committed approval response retries the exact browser request', async ({
  page,
}) => {
  function counts(): number[] {
    const text = execFileSync(
      '../.venv/bin/python',
      [
        '-c',
        "import os,sqlite3,json;from pathlib import Path;r=Path(os.environ['CASEWORK_BROWSER_ROOT']);print(json.dumps([sqlite3.connect(r/'tickets.sqlite3').execute('SELECT COUNT(*) FROM tickets').fetchone()[0],sqlite3.connect(r/'orders.sqlite3').execute('SELECT COUNT(*) FROM annotations').fetchone()[0]]))",
      ],
      { encoding: 'utf8' },
    );
    const value: unknown = JSON.parse(text);
    if (
      !Array.isArray(value) ||
      value.length !== 2 ||
      !value.every((v) => typeof v === 'number')
    )
      throw new Error('Invalid counts.');
    return value as number[];
  }
  const before = counts();
  const requests: { key: string; body: string }[] = [];
  await page.route('**/decisions', async (route) => {
    const request = route.request();
    if (request.method() !== 'POST') {
      await route.continue();
      return;
    }
    requests.push({
      key: request.headers()['idempotency-key'] ?? '',
      body: request.postData() ?? '',
    });
    if (requests.length === 1) {
      // Forward the real request and wait for the actual commit, then lose only its browser response.
      const response = await route.fetch();
      expect(response.status()).toBe(200);
      await route.abort('failed');
    } else await route.continue();
  });
  await page.goto('/');
  await page
    .getByRole('button', { name: 'Open delayed delivery example' })
    .click();
  await page.getByRole('button', { name: 'Approve fictional action' }).click();
  await expect(
    page.getByRole('button', { name: 'Retry saved request' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Retry saved request' }).click();
  await expect(page.getByRole('status')).toHaveText('completed');
  await expect(
    page.getByText('Ticket confirmed', { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText('Order annotation confirmed', { exact: true }),
  ).toBeVisible();
  expect(requests).toHaveLength(2);
  expect(requests[1]).toEqual(requests[0]);
  expect(requests[0]?.key).not.toBe('');
  expect(counts()).toEqual(before.map((v) => v + 1));
});
