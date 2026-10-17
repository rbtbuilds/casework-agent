import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { parseCase } from "./src/api/schema";

test("record evidence, exact approval and confirmed HTTP effects", async ({
  page,
  request,
  browser,
}) => {
  const mode = process.env.CASEWORK_RECORDING_MODE;
  const root = process.env.CASEWORK_BROWSER_ROOT;
  if (!root || (mode !== "model" && mode !== "fixture"))
    throw new Error("Explicit recording mode/root required.");
  const start = performance.now();
  const chapters: { seconds: number; title: string; detail: string }[] = [];
  const label =
    mode === "model"
      ? "ACTUAL QWEN / synthetic records"
      : "FIXTURE RECOVERY / no model inference";
  const chapter = (title: string, detail: string) =>
    chapters.push({
      seconds: (performance.now() - start) / 1000,
      title,
      detail,
    });
  function persisted() {
    const raw = execFileSync(
      "../.venv/bin/python",
      [
        "-c",
        "import os,sqlite3,json;from pathlib import Path;r=Path(os.environ['CASEWORK_BROWSER_ROOT']);out={};\nfor name,table in [('tickets','tickets'),('orders','annotations')]:\n c=sqlite3.connect((r/(name+'.sqlite3')).resolve().as_uri()+'?mode=ro',uri=True);out[name]={'effects':[json.loads(x[0]) for x in c.execute('SELECT payload FROM '+table)],'journals':[json.loads(x[0]) for x in c.execute('SELECT payload FROM idempotency')]};c.close()\nc=sqlite3.connect((r/'.runtime/app.sqlite3').resolve().as_uri()+'?mode=ro',uri=True);out['runs']=[json.loads(x[0]) for x in c.execute('SELECT payload_json FROM agent_runs')];c.close();print(json.dumps(out))",
      ],
      { encoding: "utf8" },
    );
    const data: unknown = JSON.parse(raw);
    if (!data || typeof data !== "object")
      throw new Error("Invalid database capture.");
    return data as {
      tickets: { effects: unknown[]; journals: unknown[] };
      orders: { effects: unknown[]; journals: unknown[] };
      runs: unknown[];
    };
  }
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  chapter("Read evidence. Review the exact proposal. Approve once.", label);
  await page.goto("/");
  await page
    .getByRole("combobox", { name: "Appearance" })
    .selectOption("light");
  await page
    .getByRole("combobox", { name: "Decision engine" })
    .selectOption(mode);
  await page.waitForTimeout(2500);
  const creation = page.waitForResponse(
    (r) => r.url().endsWith("/v1/cases") && r.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "Open delayed delivery example" })
    .click();
  const created = parseCase(await (await creation).json());
  expect(created.mode).toBe(mode);
  chapter(
    mode === "model"
      ? "Qwen gathers scoped evidence and evaluates six conditions."
      : "Fixture decision; real API, worker and three HTTP services.",
    mode === "model"
      ? "Live inference at original speed. No fixture fallback or case replay."
      : "Fault injection drops both write responses AFTER their remote transactions commit.",
  );
  await page
    .getByRole("button", { name: "Approve fictional action" })
    .waitFor({ state: "visible", timeout: 150000 });
  const ready = parseCase(
    await (
      await request.get(`http://127.0.0.1:8112/v1/cases/${created.id}`)
    ).json(),
  );
  expect(ready.error).toBeNull();
  expect(ready.evidence).toHaveLength(3);
  expect(ready.operations).toEqual([]);
  const before = persisted();
  expect(before.tickets.effects).toHaveLength(0);
  expect(before.orders.effects).toHaveLength(0);
  expect(before.tickets.journals).toHaveLength(0);
  expect(before.orders.journals).toHaveLength(0);
  if (!ready.proposal) throw new Error("No proposal.");
  const proposal = ready.proposal;
  chapter(
    "Evidence is visible; zero tickets or annotations before approval.",
    "Verified against both remote SQLite stores and journals. Displayed prose is application-rendered.",
  );
  await page
    .getByText(mode === "model" ? "Actual local model" : "Fixture workflow", {
      exact: true,
    })
    .last()
    .scrollIntoViewIfNeeded();
  await page.waitForTimeout(2500);
  const sources = page.getByText("Inspect source and hash", { exact: true });
  await sources.first().click();
  await page.waitForTimeout(3000);
  await sources.first().click();
  await page
    .getByRole("heading", { name: "Exact internal note" })
    .scrollIntoViewIfNeeded();
  chapter(
    "Approve the displayed note, source versions and proposal hash.",
    "Approval is an automated browser action for this recording; no human factual sign-off is implied.",
  );
  await page.waitForTimeout(4000);
  const approvalResponse = page.waitForResponse(
    (r) => r.url().endsWith("/decisions") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Approve fictional action" }).click();
  const approval = await approvalResponse;
  expect(approval.status()).toBe(200);
  const approvalBody: unknown = approval.request().postDataJSON();
  expect(approvalBody).toEqual({
    proposal_id: proposal.id,
    proposal_hash: proposal.hash,
    expected_case_version: ready.version,
    decision: "approve",
  });
  chapter(
    mode === "model"
      ? "Exact approval committed; the worker sends the saved operations."
      : "Lost responses are unknown; the worker reconciles the SAME saved keys.",
    mode === "model"
      ? "The model has no write tools. Approval grants only the two displayed fictional effects."
      : "Recovery is automatic. The durable timeline retains both uncertainty events.",
  );
  await expect(page.getByRole("status")).toHaveText("completed", {
    timeout: 20000,
  });
  await expect(
    page.getByText("Ticket confirmed", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Order annotation confirmed", { exact: true }),
  ).toBeVisible();
  const final = parseCase(
    await (
      await request.get(`http://127.0.0.1:8112/v1/cases/${created.id}`)
    ).json(),
  );
  const after = persisted();
  expect(after.tickets.effects).toHaveLength(1);
  expect(after.orders.effects).toHaveLength(1);
  expect(final.operations).toHaveLength(2);
  for (const [index, service] of [after.tickets, after.orders].entries()) {
    const op = final.operations[index];
    if (!op) throw new Error("Missing operation.");
    expect(op.state).toBe("succeeded");
    expect(op.attempts).toBe(1);
    expect(service.journals).toEqual([
      expect.objectContaining({
        key: op.key,
        request_hash: op.request_hash,
        outcome: "succeeded",
        response_json: op.response_json,
      }),
    ]);
    expect(service.effects).toEqual([op.response_json]);
  }
  expect(
    final.events.filter((e) => e.kind === "outcome_unconfirmed"),
  ).toHaveLength(mode === "fixture" ? 2 : 0);
  if (mode === "model")
    expect(after.runs).toEqual([
      expect.objectContaining({
        adapter: "model",
        protocol_version: "casework-json-schema-v5-isolated-conditions",
        status: "claims_and_decision_validated",
        assessment_diagnostics: expect.objectContaining({
          fields_correct: 6,
          mismatched_fields: [],
          reason_supported: true,
        }),
        inference_calls: expect.arrayContaining([
          expect.objectContaining({
            ordinal: 10,
            phase: "decision",
            status: "received",
          }),
        ]),
      }),
    ]);
  chapter(
    "Confirmed: one ticket, one annotation, one send per operation.",
    label +
      " | Journal keys, request hashes and effect bodies match; no duplicate writes.",
  );
  await page
    .getByText("Order annotation confirmed", { exact: true })
    .scrollIntoViewIfNeeded();
  await page.waitForTimeout(4500);
  if (mode === "fixture") {
    await page
      .getByRole("heading", { name: "Durable timeline" })
      .scrollIntoViewIfNeeded();
    await expect(
      page.getByText("outcome unconfirmed", { exact: true }),
    ).toHaveCount(2);
    await page
      .getByText("outcome unconfirmed", { exact: true })
      .last()
      .scrollIntoViewIfNeeded();
    await expect(
      page.getByText("outcome unconfirmed", { exact: true }).last(),
    ).toBeInViewport();
    chapter(
      "Both lost responses remain in the durable audit timeline.",
      "Remote journals confirmed the existing effects. No replacement key or second send was needed.",
    );
    await page.waitForTimeout(5000);
  }
  expect(errors).toEqual([]);
  await page.screenshot({ path: `${root}/completed.png`, fullPage: true });
  const capturedWallSeconds = (performance.now() - start) / 1000;
  const video = page.video();
  if (!video) throw new Error("Recording was not enabled.");
  await page.close();
  await video.saveAs(`${root}/walkthrough.webm`);
  const captionContext = await browser.newContext({
    viewport: { width: 1440, height: 100 },
  });
  const captions = await captionContext.newPage();
  for (const [index, item] of chapters.entries()) {
    await captions.setContent(
      `<body style="margin:0;background:#0b1220;color:#f1f5f9;font:18px/1.5 system-ui;padding:15px 24px;box-sizing:border-box"><strong>${item.title}</strong><div style="color:#cbd5e1;font-size:16px">${item.detail}</div></body>`,
    );
    await captions.screenshot({ path: `${root}/caption-${index}.png` });
  }
  await captionContext.close();
  writeFileSync(
    `${root}/recording.json`,
    JSON.stringify(
      {
        mode,
        label,
        source_commit: execFileSync("git", ["rev-parse", "HEAD"], {
          encoding: "utf8",
        }).trim(),
        source_dirty:
          execFileSync("git", ["status", "--porcelain"], {
            encoding: "utf8",
          }).trim() !== "",
        scenario: "fixtures/scenarios/dev-delay-01.json",
        provenance:
          "New automated browser demonstration on an exposed example, not unseen evaluation. Uncut recording; caption strip added below the viewport.",
        chapters,
        captured_wall_seconds: capturedWallSeconds,
        before,
        after,
        approval: {
          body: approvalBody,
          key: approval.request().headers()["idempotency-key"],
        },
        case: final,
        browser_errors: errors,
        human_review: "pending",
      },
      null,
      2,
    ) + "\n",
  );
});
