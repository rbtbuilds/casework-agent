import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { parseCase } from "../src/api/schema";

test("actual local Qwen reads, approval and dropped-write recovery", async ({
  page,
  request,
}) => {
  test.skip(
    process.env.CASEWORK_REAL_MODEL !== "1",
    "Requires the pinned local weights and exclusive shared model lease.",
  );
  test.setTimeout(180000);
  const root = process.env.CASEWORK_BROWSER_ROOT;
  if (!root) throw new Error("Browser runtime root missing.");
  function counts(): number[] {
    const raw = execFileSync(
      "../.venv/bin/python",
      [
        "-c",
        "import os,sqlite3,json;from pathlib import Path;r=Path(os.environ['CASEWORK_BROWSER_ROOT']);print(json.dumps([sqlite3.connect(r/'tickets.sqlite3').execute('SELECT COUNT(*) FROM tickets').fetchone()[0],sqlite3.connect(r/'orders.sqlite3').execute('SELECT COUNT(*) FROM annotations').fetchone()[0]]))",
      ],
      { encoding: "utf8" },
    );
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed) || !parsed.every((n) => typeof n === "number"))
      throw new Error("Invalid persisted counts.");
    return parsed as number[];
  }
  const before = counts();
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await page
    .getByRole("combobox", { name: "Decision engine" })
    .selectOption("model");
  const createdResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/v1/cases") &&
      response.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "Open delayed delivery example" })
    .click();
  const created = parseCase(await (await createdResponse).json());
  expect(created.mode).toBe("model");
  await page
    .getByRole("button", { name: "Approve fictional action" })
    .or(page.getByRole("alert"))
    .first()
    .waitFor({ state: "visible", timeout: 150000 });
  const ready = parseCase(
    await (
      await request.get(`http://127.0.0.1:8112/v1/cases/${created.id}`)
    ).json(),
  );
  expect(
    ready.error,
    "Actual model gathering must succeed without fixture fallback.",
  ).toBeNull();
  expect(ready.proposal?.action).toBe("open_investigation");
  expect(ready.evidence).toHaveLength(3);
  expect(counts()).toEqual(before);
  await expect(
    page.getByText("Actual local model", { exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "../.runtime/evidence/qwen-proposal.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Approve fictional action" }).click();
  await expect(page.getByRole("status")).toHaveText("completed", {
    timeout: 20000,
  });
  await expect(
    page.getByText("Ticket confirmed", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Order annotation confirmed", { exact: true }),
  ).toBeVisible();
  expect(counts()).toEqual(before.map((n) => n + 1));
  const final = parseCase(
    await (
      await request.get(`http://127.0.0.1:8112/v1/cases/${created.id}`)
    ).json(),
  );
  expect(
    final.events.filter((event) => event.kind === "outcome_unconfirmed"),
  ).toHaveLength(2);
  expect(final.operations).toHaveLength(2);
  expect(
    final.operations.every(
      (operation) =>
        operation.state === "succeeded" && operation.attempts === 1,
    ),
  ).toBe(true);
  const traces = execFileSync(
    "../.venv/bin/python",
    [
      "-c",
      "import os,sqlite3,json;from pathlib import Path;r=Path(os.environ['CASEWORK_BROWSER_ROOT']);c=sqlite3.connect(r/'.runtime/app.sqlite3');print(json.dumps([json.loads(v[0]) for v in c.execute('SELECT payload_json FROM agent_runs')]))",
    ],
    { encoding: "utf8" },
  );
  const runs: unknown = JSON.parse(traces);
  expect(runs).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        adapter: "model",
        usage_tokens: expect.any(Number),
        protocol_version: "casework-json-schema-v5-isolated-conditions",
        status: "claims_and_decision_validated",
        assessment_diagnostics: expect.objectContaining({
          mismatched_fields: [],
          reason_supported: true,
          fields_correct: 6,
        }),
        model_assessment: {
          order_in_transit: true,
          shipment_delayed: true,
          no_policy_exception: true,
          no_conflicting_or_terminal_events: true,
          timestamps_known_and_consistent: true,
          age_at_least_48_hours: true,
        },
        inference_calls: expect.arrayContaining([
          expect.objectContaining({
            ordinal: 10,
            phase: "decision",
            status: "received",
          }),
        ]),
      }),
    ]),
  );
  await page.screenshot({
    path: "../.runtime/evidence/qwen-completed.png",
    fullPage: true,
  });
  writeFileSync(
    `${root}/model-browser-evidence.json`,
    JSON.stringify(
      {
        verification:
          "actual model through browser, API, HTTP reads and recovered writes",
        before,
        after: counts(),
        case: final,
        runs,
        browser_errors: errors,
      },
      null,
      2,
    ),
  );
  expect(errors).toEqual([]);
});
