# Local runbook

Run every command from the root of this repository. Nothing here requires a cloud account or a paid service. All business records are original fiction.

## Bootstrap and run

Use Python 3.12 with uv. CI uses Node 24 LTS. This Mac was also tested with Node 26.7.0; Vite 8 accepts Node >=22.12. Do not replace a global runtime.

```sh
uv sync --locked
npm --prefix web ci
uv run python scripts/dev.py start
uv run python scripts/dev.py status
uv run python scripts/dev.py stop
```

Open <http://127.0.0.1:5112>. Choose Fixture workflow, open the delayed delivery example, inspect evidence and approve the exact fictional note. Both write outcomes must say confirmed. The default demo databases persist under `.runtime/dev`. A new isolated demonstration uses `--root .runtime/demo-N` on start/status/stop. Existing databases are never reset automatically.

`dev start` detaches deliberately and writes `processes.json` with PID, process start time, actual arguments and an environment nonce. `dev run` stays in the foreground and stops its verified children on Ctrl-C or SIGTERM. Stop refuses changed identities. Busy reserved ports fail before any launch. Never use a broad process kill or move to a different port.

| Service | Loopback port |
| --- | --- |
| Workbench | 5112 |
| Application and single worker | 8112 |
| Orders | 8212 |
| Carrier | 8312 |
| Tickets | 8412 |

The API process owns one worker task and a separate five-second heartbeat task. The database lease expires after 30 seconds; a takeover increments its generation. This couples API and worker availability, but ownership and saved operation state survive a process restart. HTTP reads and model work never hold a database transaction.

## Tests

Stop the demo before tests: process tests use the same reserved ports. Run Python and browser process suites sequentially.

```sh
uv run ruff check .
uv run pyright
uv run pytest -q
npm --prefix web run typecheck
npm --prefix web test -- --run
npm --prefix web run build
PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" web/node_modules/.bin/playwright install chromium
PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e
uv run python scripts/export_contracts.py
npm --prefix web run contracts
git diff --exit-code -- contracts/openapi.json web/src/api/generated.ts web/src/api/case.schema.json
```

Browser runs create fresh `.runtime/browser-*` databases and stop their foreground owner. Model process unit tests use scripted/invalid children and are not inference evidence. Temporary pytest data stays in this project's `.runtime/pytest`.

## Local Qwen

```sh
uv sync --locked --extra model
uv run --extra model python scripts/model_session.py prepare
uv run --extra model python scripts/model_session.py probe
uv run --extra model python scripts/dev.py start
```

The public download resolves an immutable revision and hashes files under this project's `.runtime/models`. It does not upload anything. `prepare` makes network requests to the public model host; do not run it when reproducing a frozen report unless deliberately preparing the same snapshot. Model dependencies are optional on Apple Silicon. Fixture mode remains available without them. The UI never silently substitutes fixture decisions for a failed model run. Health reports protocol availability only after a successful saved probe; inspect the probe result itself.

Before loading weights, `ModelSession` atomically creates `/tmp/bentolabs-portfolio-ml.lock`. Its owner record includes project, PID, process start time, UTC start, purpose and random token. If occupied, the model case fails explicitly with `model_busy`; do not steal or delete it. Model weights live only in an owned child process. Normal completion, cancellation and startup failure wait for child exit before releasing the matching token. If cleanup fails, preserve the lease and investigate that exact recorded process. The protocol is JSON lines over pipes; no model server port is used.

## Evaluation

```sh
uv run python -m eval.runner --manifest fixtures/manifests/holdout.json --mode fixture --output .runtime/reports/fixture.json
uv run --extra model python scripts/model_session.py evaluate --manifest fixtures/manifests/holdout.json --output .runtime/reports/qwen.json
```

Each case uses fresh isolated databases and three actual HTTP processes. The model benchmark holds one lease and one model child throughout; business calls still cross HTTP. Output includes per-case traces and an incremental progress file. Oracle fields and split labels never enter the agent context. Six stale cases expect zero writes; 24 expect a completed ticket/annotation pair. An aborted or busy run is not a passing report. Reports remain ignored until deliberately inspected and curated. No monetary savings or customer impact is inferred.

## Recovery and operator actions

A failed read leaves no approved write. Repropose is explicit. The queue briefly returns `new` before the worker starts `gathering`; cancelled or interrupted gathering cannot publish over a later state.

Before the first write claim, cancellation and claiming race inside `BEGIN IMMEDIATE`. Afterwards cancellation returns `execution_started` and does not delete remote effects. A timeout or lost response is unknown, even when the remote already committed. Recovery queries that operation's saved key and hash. A matching journal confirms the result. A 404 permits only an identical same-key replay because each mock journals atomically with its domain change. At most three sends are persisted per operation. Unreachable or mismatched journals remain visible as Outcome unconfirmed.

The Reconcile uncertain outcome button persists an audited, idempotent job. It grants no new authority and cannot change a saved payload. An order version conflict after a confirmed ticket leaves a partial result for review; no rollback is attempted. On restart, unfinished sends become unknown and reconcile before new claims. Interrupted model gathering becomes `agent_interrupted`; explicitly request a new proposal.

For manual API use, fetch `/v1/cases/{id}`, use its current version, and retain the same request body and Idempotency-Key for retries. Decision requests also require the exact displayed proposal ID and hash. Old or modified approvals return 409. Repeated identical successful requests return their original response, which can be older than the current case; fetch again for current status.

## Database preservation

Each service owns its own SQLite file; the application uses only HTTP to reach mocks. Schema version 1 and WAL/foreign keys are enabled on connection. JSON records validate against typed contracts. Stop verified owned services before copying a backup. Preserve the whole runtime directory, including SQLite WAL/SHM sidecars if present. Never copy only a live main database file. Startup schema failures prevent readiness; restore a known complete backup rather than editing migration history.

The original fixtures can seed a fresh runtime directory. They do not overwrite an existing database. There is no production-like reset endpoint. Unknown real-world mutations, journal expiry, cross-service atomic snapshots and cross-service rollback are outside this simulation's guarantees.
