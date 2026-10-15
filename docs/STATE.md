# Casework Agent state

Updated:2026-10-15. All ten implementation tasks and the final review fix pass are complete locally. Fixture acceptance passes;the selected Qwen model fails the measured quality gate. Work stayed inside this independent child on `feat/casework-agent-v1`.

## Verified implementation

| Task | Result |
| --- | --- |
|1 Storage/API |Typed contracts,atomic migrations1/2,WAL and health |
|2 Independent services |Real orders/carrier/tickets HTTP processes with separate SQLite journals |
|3 Bounded reads/fixture |Case scope,policy checks,three evidence sources |
|4 Qwen/MLX path |Pinned public snapshot,owned subprocess,resource lease,strict JSON loop |
|5 Exact approvals |Immutable cited snapshot/hash/source versions/policy/expiry and replay |
|6 Execution/recovery |Persist-before-send,worker generation,unknown/partial outcomes and same-key reconciliation |
|7 API/lifecycle/contracts |Admitted scenario tuple,CORS/body/key errors,owned process identities,generated TS/runtime schemas |
|8 Workbench |Both themes,mobile/desktop,exact approval,named outcomes and keyboard controls |
|9 Failure/browser matrix |53Python tests and3real browser flows,including expiry renewal and lost committed response retry |
|10 Evaluation/docs |60frozen scenarios,separate fixture/model evidence,runbook,case study,CI and screenshots |

## Final checks

Fresh full source verification passed53pytest tests,Ruff,strict Pyright,strict TypeScript,5Vitest tests,and production build. Contract regeneration produced no diff. The three Playwright flows passed against actual local services:normal approval/replay with both remote response drops;expiry then renewal;and a browser response lost after real API commit followed by identical body/key retry. Tested Axe scans reported zero violations in both themes and at375px/1440px,with reduced motion. No page errors were observed in the captured flow.

A clean archive of `1da911f` with fresh `.venv` and `web/node_modules` passed locked uv/npm installation,all strict checks,53pytest tests,5component tests,build and all3browser flows. The prior clean attempt failed37temporary-fixture setups because `.runtime` was absent;the pytest bootstrap fix was verified by this fresh rerun. See [clean-checkout evidence](evidence/clean-checkout.json).

Node26.7.0 is the tested local exception;CI targetsNode24 and has not run externally because nothing was pushed. Python3.12.14,uv0.12.5,Vite8.3.4,React19.3.1,TypeScript5.9.3,MLX LM0.32.0,MLX0.32.4. Hardware:Apple M5 Pro,24GiB. All resolved dependencies are locked. Source ASCII and relative documentation links were checked.

## Frozen final measurement

Both latest reports measured committed source `1da911fb12bb896e750248a67f22345bf3d7892b`,with dirty=false. The prompt,model and held-out inputs were unchanged after their initial failed run. The original in-progress reports remain as `initial-fixture-full.json` and `initial-qwen-full.json` for provenance.

| Metric | Fixture | Actual Qwen/MLX |
| --- | --- | --- |
|Valid actions |30/30 |0/30 |
|Expected final states/counts |30/30 |0/30 |
|Authorised completions |24/24 |0/24 |
|Unapproved/duplicate effects |0/0 |0/0 |

The actual model produced30failed cases;the quality thresholds27/30actions,27/30outcomes and22/24completions are not met. Invalid outputs stopped before approval or writes. Model human claim review remains pending;unsupported_claims is null. The actual smoke output omitted the required arguments field even though weights loaded. No fixture fallback or model substitution occurred.

Latest model load:4.136s. Warm failed-case latency p50:4.057s,p95 nearest rank:8.055s across30cases. Tokenizer-counted input+output usage:62512. These are failed-task timings,not productive throughput or monetary savings. Model child exit was confirmed before releasing its matching shared lease.

Model:`Qwen/Qwen2.5-1.5B-Instruct`,revision`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`,9hashed files. Held-out manifest SHA-256:`6be686fcff49b9d5b5bad120ac0d96b5244cfb4f585f9bd0b2d821337e4e1ad8`. Latest fixture report SHA-256:`e0c36705bfaa285b83fc678d9da42798b9a6326fc8d37f4991ec9537e3b9755a`. Latest Qwen report SHA-256:`3916875d61c9b9200db58d4dd4ccedb3be8ae1447b2ddbe2755acd851cf45b2c`. Full case traces,split hashes,lock hashes,Git/hardware provenance and summaries are curated under docs/evidence;weights and runtime bulk remain ignored.

## Review and boundaries

One fresh judgment reviewer examined d6aa779..009b67e and found6Important,noCritical,noMinor issues. The single fix pass addressed every finding with focused regressions and the complete suite. Evidence/run-generation/tuple/expiry regressions were observed failing before their fixes;browser retry was a coverage gap in existing behavior and now has real transport-loss proof. No second reviewer was dispatched. All execution decisions,costs and declined-review boundaries are in [ENGINEERING-DECISIONS](ENGINEERING-DECISIONS.md). No Minor issues were deferred.

Manual screen-reader testing and human factual-claim review remain unperformed. The model quality gate fails. There is no distributed exactly-once guarantee,cross-service rollback,public authentication or production validation. The walkthrough file is a presenter guide;no two-minute recording is claimed.

Owned services from tests and benchmarks were stopped;no persistent demo is intentionally left running. Check actual listeners/status before launching. Reserved loopback ports remain8112/5112/8212/8312/8412. No sibling,parent,resume,vault,registry or machine configuration was changed. No publication,push,deployment,model upload,paid resource or external message was performed.

## Local history and next action

Planning d6aa779;Task1ce85f6e;Task2 4938667/ec3c145;Task3ae7c8f0;Task4 8801131;Task5 395ec54;Task6 6c70f17;Task7 8a4c49c;Task8 bbd7851;Task9 2608b76;Task10 009b67e;review fixes1da911f. The final evidence-only commit follows this measured source. Earlier Task2 lint errors were corrected immediately and freshly verified;shared pytest housekeeping warnings were resolved without manually changing foreign data.

To run the local demo:from this project,`uv sync --locked`, `npm --prefix web ci`,then `uv run python scripts/dev.py start`;open http://127.0.0.1:5112. Stop with `uv run python scripts/dev.py stop`. Keep fixture/model labels visible. Any future model improvement needs development-set work and a separately reviewed evaluation;do not tune against this failed holdout. Publication still requires Matthew's specific authorization.
