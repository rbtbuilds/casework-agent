# Local runbook

Run these commands from the repository root. The demo uses synthetic business records and requires no cloud credentials.

## Bootstrap and run

Use Python 3.12 with uv and Node.js 24 LTS, matching the CI configuration. Fixture verification covers Ubuntu and macOS; optional MLX inference requires Apple Silicon. Benchmark hardware and runtime versions are recorded in [MODEL-CONFIG](MODEL-CONFIG.md).

```sh
uv sync --locked
npm --prefix web ci
uv run python scripts/dev.py start
uv run python scripts/dev.py status
uv run python scripts/dev.py stop
```

Open <http://127.0.0.1:5112>. Choose Fixture workflow, open the delayed delivery example, inspect evidence and approve the exact fictional note. Both write outcomes must say confirmed. The default demo databases persist under `.runtime/dev`. A new isolated demonstration uses `--root .runtime/demo-N` on start/status/stop. Existing databases are never reset automatically.

`dev start` detaches deliberately and writes `processes.json` with PID, process start time, actual arguments and an environment nonce. `dev run` stays in the foreground and stops its verified children on Ctrl-C or SIGTERM, including an interruption during service readiness. Interrupted `dev start` also cleans up the children created by that attempt. Stop refuses changed identities. Busy reserved ports fail before any launch. Never use a broad process kill or move to a different port.

| Service                       | Loopback port |
| ----------------------------- | ------------- |
| Workbench                     | 5112          |
| Application and single worker | 8112          |
| Orders                        | 8212          |
| Carrier                       | 8312          |
| Tickets                       | 8412          |

The API process owns one worker task and a separate five-second heartbeat task. The database lease expires after 30 seconds; a takeover increments its generation. This couples API and worker availability, but ownership and saved operation state survive a process restart. HTTP reads and model work never hold a database transaction. Dependency responses stream under a 32 KiB cap. Local integrations accept identity encoding only. Read attempts have a two-second total deadline; writes and journal reads have three seconds. The 120-second model tool-loop deadline includes awaited tools.

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

The default download selects pinned `mlx-community/Qwen3-14B-4bit` and hashes its weights, tokenizer, configuration and chat template under this project's `.runtime/models`. It does not upload anything. `prepare` makes network requests to the public model host; use the profile and source revision recorded by the report when reproducing a benchmark. Model dependencies are optional on Apple Silicon. Fixture mode remains available without them. The UI never silently substitutes fixture decisions for a failed model run. Health reports protocol availability only after a saved probe matching the selected snapshot and protocol version; inspect the probe result itself. The probe does not establish task quality.

Before loading weights, `ModelSession` atomically creates `/tmp/bentolabs-portfolio-ml.lock`. Its owner record includes project, PID, process start time, UTC start, purpose and random token. If occupied, the model case fails explicitly with `model_busy`; do not steal or delete it. Model weights live only in an owned child process. Normal completion, cancellation and startup failure wait for child exit before releasing the matching token. If cleanup fails, preserve the lease and investigate that exact recorded process. The protocol is JSON lines over pipes; no model server port is used.

The default profile is `qwen3-14b` (approximately 8.3 GB of weights). `prepare --profile qwen3-4b` retains the failed 4B comparison. `prepare --profile baseline1.5b` and `prepare --profile qwen7b` select the preserved development comparisons explicitly. Changing profiles requires another probe. The original 0/30 report used the old adapter at its recorded source revision; selecting old weights with current code is a different experiment.

The actual-model browser check is opt-in and requires the pinned weights and an available shared lease. Stop the developer stack first. This runs all browser flows together, including Qwen proposal generation and both post-commit response drops:

```sh
CASEWORK_REAL_MODEL=1 PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e
```

Without that environment variable, the model check is explicitly skipped and the fixture browser suite runs without model dependencies. No browser business response is substituted with a fixture in the opt-in model check.

## Evaluation

```sh
uv run python -m eval.runner --manifest fixtures/manifests/v3-challenge.json --mode fixture --output .runtime/reports/fixture-v3.json
uv run --extra model python scripts/model_session.py evaluate --manifest fixtures/manifests/v3-challenge.json --output .runtime/reports/qwen-v3.json
```

Each case uses fresh isolated databases and three actual HTTP processes. The model benchmark holds one lease and one model child throughout; business calls still cross HTTP. Output includes per-case traces and an incremental progress file. Oracle fields and split labels never enter the agent context. Six stale cases expect zero writes; 24 expect a completed ticket/annotation pair. An aborted or busy run is not a passing report. Reports remain ignored until deliberately inspected and curated. No monetary savings or customer impact is inferred.

## Recovery and operator actions

A failed read leaves no approved write. Repropose is explicit. The queue briefly returns `new` before the worker starts `gathering`; cancelled or interrupted gathering cannot publish over a later state.

Before the first write claim, cancellation and claiming race inside `BEGIN IMMEDIATE`. Afterwards cancellation returns `execution_started` and does not delete remote effects. A timeout or lost response is unknown, even when the remote already committed. Recovery queries that operation's saved key and hash. A matching journal confirms the result only when its successful response includes an explicit valid remote ticket or annotation ID. Missing or unusable IDs remain unknown; they are never generated by the application. A 404 permits only an identical same-key replay because each mock journals atomically with its domain change. At most three sends are persisted per operation. Unreachable or mismatched journals remain visible as Outcome unconfirmed.

The Reconcile uncertain outcome button persists an audited, idempotent job. It grants no new authority and cannot change a saved payload. An order version conflict after a confirmed ticket leaves a partial result for review; no rollback is attempted. On restart, unfinished sends become unknown and reconcile before new claims. Gathering success/failure/trace writes also require the saved run ID and current worker generation. Expired unclaimed proposals become stale and can be explicitly renewed. Interrupted model gathering becomes `agent_interrupted`; explicitly request a new proposal.

For manual API use, fetch `/v1/cases/{id}`, use its current version, and retain the same request body and Idempotency-Key for retries. Decision requests also require the exact displayed proposal ID and hash. Old or modified approvals return 409. Repeated identical successful requests return their original response, which can be older than the current case; fetch again for current status.

## Database preservation

Each service owns its own SQLite file; the application uses only HTTP to reach mocks. Versioned migrations 1 and 2 and WAL/foreign keys are enabled on connection. Migration 2 adds gathering run ownership without replacing business records. JSON records validate against typed contracts. Stop verified owned services before copying a backup. Preserve the whole runtime directory, including SQLite WAL/SHM sidecars if present. Never copy only a live main database file. Startup schema failures prevent readiness; restore a known complete backup rather than editing migration history.

The original fixtures can seed a fresh runtime directory. They do not overwrite an existing database. There is no production-like reset endpoint. Unknown real-world mutations, journal expiry, cross-service atomic snapshots and cross-service rollback are outside this simulation's guarantees.

Browser expiry uses a constructor-injected FileClock from an explicitly created test fixture clock.txt. It advances through an atomic fixture-file replacement; no reset/time endpoint is exposed. Browser response-loss tests forward the real approval request and drop only its response after the API commits.

## V5 trace and reproduction boundaries

The current first-run model evidence is [v5](../EVALUATION.md#first-frozen-v5-measurement). Published challenge reruns are reproductions. Use the recorded manifest, immutable model revision and protocol when comparing results; never overwrite frozen reports.

A normal v5 case makes ten model requests (three reads, six isolated conditions, one choice), with at most one global syntax repair and an eleven-request maximum under the unchanged 120-second case deadline. `inference_calls` contains exact request boundaries, schemas, raw replies and partial failures; `exchange` is read history only. Incorrect fields, unsupported reasons, wrong actions and invalid evidence fail without semantic feedback or replacement. Interrupted requests make aggregate usage unknown. After an attempt ends, available generated fields are still evaluated separately from missing fields.

Graceful worker cancellation persists the available trace through the saved run/current-generation guard, marks the case `agent_interrupted`, and propagates cancellation. A hard process kill cannot persist in-memory responses; restart still fails interrupted gathering rather than inventing a proposal. Saved remote-write bodies/keys and journal recovery remain independent of model traces. Explicitly repropose an interrupted case; do not automatically reuse partial answers.
