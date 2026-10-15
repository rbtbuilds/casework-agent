# Casework Agent state

Updated: 2026-10-15. All ten implementation tasks are complete. Matthew authorized a fresh review and creation/publication of the missing public GitHub repository. The public repository is [rbtbuilds/casework-agent](https://github.com/rbtbuilds/casework-agent), with default branch `main`. Source and documentation were pushed at `9140ba8`; GitHub CI status is recorded below. Work remains scoped to this independent checkout on `feat/casework-agent-v1`.

## Current verification

The pre-publication review found six residual issues and all received focused regressions and fixes. A follow-up identified a narrower interruption window between process creation and ownership registration; its additional real-process regression failed before the supervisor-handler deferral fix. A strengthened check also rejects inherited blocked signals and forced termination. See [the review record](REVIEW-2026-10-15.md) and [engineering decisions](ENGINEERING-DECISIONS.md).

Final local verification passes **73 Python tests**, **eight component tests**, Ruff, strict Pyright, strict TypeScript including tests, and the production build. All six review findings are closed by the same reviewer after focused follow-up. The three actual-service browser flows also pass after the port-owning Python suite. Regenerating all three contract artifacts reproduces their current bytes. Reviewed runtime source is commit `33c3efa3a46b0853010134774262c11eb05f6529`; later documentation commits do not change that source.

Commands: `uv run --no-sync ruff check .`; `uv run --no-sync pyright`; `uv run --no-sync pytest -q`; `npm --prefix web run typecheck`; `npm --prefix web test -- --run`; `npm --prefix web run build`; `PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e`; `uv run --no-sync python scripts/export_contracts.py`; `npm --prefix web run contracts`.

A scan of 196 tracked/new nonignored publication files found no credential-pattern matches. A separate scan of 287 historical Git blobs also found none. These are bounded pattern scans, not a guarantee that every possible secret format is detectable. Frozen full reports match their original bytes and relative Markdown links resolve.

The browser suite exercises approval/replay with both remote response drops, expiry/renewal, and a browser response lost after the actual API commit followed by identical body/key retry. Tested Axe scans have zero findings in both themes and at 375px/1440px with reduced motion. Mobile and desktop captures were visually inspected. Manual screen-reader testing remains unperformed.

Python 3.12.14, uv 0.12.5 and Node 26.7.0 are the tested local runtimes. GitHub CI targets Python 3.12 and Node 24 on Ubuntu. Its first external run is [38810735255](https://github.com/rbtbuilds/casework-agent/actions/runs/38810735255), against `9140ba8`. The run **passed**, including locked installation, all 73 Python tests, eight component tests, all three real-service browser flows, strict checks, production build and contract regeneration. It establishes Linux/Node 24 verification separately from the local Node 26 exception. Dependencies are locked. Vite 8.3.4, React 19.3.1, TypeScript 5.9.3, MLX LM 0.32.0 and MLX 0.32.4 were used in the original implementation. Hardware: Apple M5 Pro, 24 GiB.

## Implemented scope

- FastAPI/SQLite contracts, atomic migrations 1/2, WAL, audit events and shared worker-generation fencing.
- Independent order, carrier and ticket HTTP processes with separate transactional domain/idempotency journals.
- Scoped evidence reads, deterministic conservative policy, immutable proposals and exact evidence/version/hash/policy/expiry-bound approval.
- Persist-before-send operation keys and payloads, explicit unknown/partial outcomes, bounded same-key reconciliation and cancellation arbitration.
- Pinned Qwen/MLX subprocess, shared machine lease, strict read-tool JSON protocol and separately labelled fixture baseline.
- Responsive light/dark workbench with exact approval, per-operation outcomes, keyboard controls, monotonic response handling and saved-request retries.
- Sixty frozen synthetic scenarios, separate fixture/model evidence, reproducible evaluation, operational runbook and fixture-only CI.

## Frozen measured evidence

The latest frozen reports measured committed source `1da911fb12bb896e750248a67f22345bf3d7892b`, with dirty=false. Later publication fixes have not remeasured actual model quality. Original in-progress reports remain as `initial-fixture-full.json` and `initial-qwen-full.json`. No frozen inputs, reports or prompt were tuned to the holdout results.

| Metric                       | Fixture | Actual Qwen/MLX |
| ---------------------------- | ------- | --------------- |
| Valid actions                | 30/30   | 0/30            |
| Expected final states/counts | 30/30   | 0/30            |
| Authorized completions       | 24/24   | 0/24            |
| Unapproved/duplicate effects | 0/0     | 0/0             |

The model produced 30 `invalid_model_output` failures, missing the 27/30 action, 27/30 outcome and 22/24 completion thresholds. Invalid outputs stopped before approval or writes. Human claim review is pending; unsupported_claims is null. The actual smoke output omitted a required argument object despite successfully loading weights. No fixture fallback or model substitution occurred.

Model load: 4.136 seconds. Warm failed-case latency: p50 4.057 seconds and nearest-rank p95 8.055 seconds across 30 cases. Tokenizer-counted input/output usage: 62,512. These are failed-task timings, not productive throughput or monetary savings. The model child exited before its matching lease was released.

- Model: `Qwen/Qwen2.5-1.5B-Instruct`, revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, nine hashed files.
- Holdout manifest SHA-256: `6be686fcff49b9d5b5bad120ac0d96b5244cfb4f585f9bd0b2d821337e4e1ad8`.
- Fixture report SHA-256: `e0c36705bfaa285b83fc678d9da42798b9a6326fc8d37f4991ec9537e3b9755a`.
- Qwen report SHA-256: `3916875d61c9b9200db58d4dd4ccedb3be8ae1447b2ddbe2755acd851cf45b2c`.

Full traces, manifests, snapshot hashes and provenance are curated under `docs/evidence`. Weights, databases and bulk runtime state remain ignored. The original clean-checkout archive verification of `1da911f` is retained in [clean-checkout evidence](evidence/clean-checkout.json); it is historical evidence, not verification of later fixes.

## Boundaries and operation

The actual model quality gate fails. Human claims review, manual screen-reader testing and a recorded two-minute walkthrough remain unperformed. The walkthrough document is a presenter guide. There is no distributed exactly-once guarantee, cross-service rollback, public authentication or production validation.

The original developer demo was running when this review began. It was stopped through the ownership-checked helper for tests, then restored after the final port-owning checks with its databases intact. All five HTTP endpoints returned 200. The restored owner record is `.runtime/dev/processes.json`: orders PID 71865, carrier 71866, tickets 71867, API/worker 71868, web 71869, checked on 2026-10-15. PIDs are transient; use `scripts/dev.py status` for current ownership. Ports are API 8112, web 5112, orders 8212, carrier 8312 and tickets 8412, all loopback.

Run from the repository root: `uv sync --locked`, `npm --prefix web ci`, then `uv run python scripts/dev.py start`. Open <http://127.0.0.1:5112>. Inspect with `uv run python scripts/dev.py status`; stop with `uv run python scripts/dev.py stop`. Keep fixture/model labels visible. Future model improvements need development-set work and a new separately reviewed evaluation, not tuning against this failed holdout.

No sibling, parent, resume, vault, registry or machine configuration was changed. No deployment, model upload, paid resource or external human message was performed. Source publication is explicitly authorized; these other actions remain outside scope.

## History

Planning `d6aa779`; task 1 `ce85f6e`; task 2 `4938667`/`ec3c145`; task 3 `ae7c8f0`; task 4 `8801131`; task 5 `395ec54`; task 6 `6c70f17`; task 7 `8a4c49c`; task 8 `bbd7851`; task 9 `2608b76`; task 10 `009b67e`; original review fixes `1da911f`; original final evidence/docs `92534bb`. Pre-publication runtime fixes: `33c3efa`; publication documentation: `9140ba8`. The latter is the initial GitHub `main` commit. Local branch `feat/casework-agent-v1` tracks `origin/main`; no history was rewritten. Private vulnerability reporting is enabled. Further documentation evidence follows that verified source.
