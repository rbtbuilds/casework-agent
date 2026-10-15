# Casework Agent state

Updated:2026-10-15. Phase: implementation and verification. Work is confined to this independent child on `feat/casework-agent-v1`. The inherited resume workspace was not modified.

## Implemented tasks

| Task | Status | Evidence |
| --- | --- | --- |
|1 Typed storage/API slice |Implemented |Versioned SQLite migration,strict contracts,storage reopen and health tests |
|2 Independent mock services |Implemented |Three actual HTTP processes,atomic journals,concurrency/CAS/drop tests |
|3 Bounded tools/fixture |Implemented |Scope checks,policy boundaries,real HTTP reads |
|4 Local Qwen adapter |Implemented; model quality fails |Pinned public snapshot,owned MLX child,strict protocol and cancellation tests |
|5 Exact proposal approval |Implemented |Hash/version/TTL/policy/source/replay/rejection tests |
|6 Durable execution/recovery |Implemented |Before-send/after-commit recovery,unknown outcomes,partial conflicts,worker fencing |
|7 API/lifecycle/contracts |Implemented |Exact API/CORS/size errors,owned PID/start/argv/nonce lifecycle,generated TS/runtime schemas |
|8 Workbench |Implemented |Light/dark/mobile UI,exact-note approval,Vitest and real visual captures |
|9 Failure/browser verification |Implemented; manual accessibility limitation |Actual browser/replay/drop tests and Python failure matrix;screen reader not tested |
|10 Evaluation/runbook |Implemented; final review/clean checkout in progress |60frozen scenarios,fixture and actual Qwen reports,CI/docs/evidence |

## Verified evidence

- `uv run pytest -q`:47passed,including the additional request-size,journal mismatch,exhausted-budget and cancel-during-gather checks.
- `uv run ruff check .` and `uv run pyright`:clean,including application,mocks,evaluation,scripts and tests. Ruff formatting was applied after measurement.
- `npm --prefix web run typecheck`:passed,including components,Vitest,Playwright and configuration.
- `npm --prefix web test -- --run`:5component tests passed.
- `npm --prefix web run build`:passed.
- `PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e`:1complete actual-service test passed. Both ticket/annotation services dropped their first committed response;one pair remained. Approval replay matched,changed-body reuse returned409,keyboard approval worked,and tested Axe scans had0findings.
- Visual inspection:1440px light and375px dark captures inspected for alignment,spacing,contrast and overflow. Browser captures exist for both themes at both widths. Queue polling was corrected after inspection showed an old state.
-15expanded Python crash/approval/recovery cases passed before subsequent added budget/journal/cancellation tests. They use actual HTTP and owned fixture databases; a separate process test stops/restarts the actual API.
- Manual screen-reader testing:unperformed. No WCAG certification is claimed.

## Fixture and actual model results

Frozen30-case held-out fixture report:`docs/evidence/fixture-full.json`:30/30valid actions,30/30expected outcomes,24/24authorised completions,0unapproved writes,0duplicate effects. Six deliberate stale cases create no effects.

Actual Qwen report:`docs/evidence/qwen-full.json`:0/30valid actions,0/30expected outcomes,0/24authorised completions,30invalid_model_output failures,0writes. Human review of raw model claims is pending;unsupported_claims remains null. This fails the model quality gate. No prompt/model change was made against holdout answers.

The actual smoke output omitted required `arguments`,so its schema probe failed despite a successful runtime load. Benchmark load4.277s,warm failed-case p50=4.513s,p95=5.949s,63751tokenizer-counted input+output tokens. These are failure timings,not useful throughput. Full reports and hashes are curated;bulk runtime data remains ignored. Initial reports record a dirty implementation tree;later code changes are not implicitly remeasured.

Snapshot:`Qwen/Qwen2.5-1.5B-Instruct` revision`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`,9hashed files. MLX LM0.32.0,MLX0.32.4,Python3.12.14,Apple M5 Pro,24GiB. Actual benchmark owned one shared lease and child throughout,then confirmed exit and released its matching lease. An earlier probe returned model_busy while another project held the lock;that ownership was not disturbed.

## Runtime and isolation

Python3.12.14 via uv0.12.5. Node26.7.0 is a tested local exception;CI is configured forNode24. Vite8.3.4 accepts the installed runtime. TypeScript5.9.3 is pinned to the supported openapi-typescript7.13.0 peer range after the newest TypeScript broke generation. React19.3.1;all resolved dependencies are locked.

Ports remain API8112,web5112,orders8212,carrier8312,tickets8412 on127.0.0.1. Suites that own these ports run sequentially. `scripts/dev.py` refuses occupied ports and verifies PID,start time,argv and nonce before stopping. Owned test/benchmark services were stopped after runs;no persistent demo is intentionally left running. Check actual status before a new launch.

The API owns one asynchronous worker and separate5sheartbeat task in its single process,with a durable30slease and incrementing generation. This intentionally couples availability while retaining one execution owner. Explicit reproposal queues`new`before the worker enters`gathering`. JSON records carry validated contract fields;SQLite indexes and constraints carry identifiers,state,versions,operation keys and relationships.

## Local commits

Planning baseline`d6aa779`;Task1`ce85f6e`;Task2`4938667`and correction`ec3c145`;Task3`ae7c8f0`;Task4`8801131`;Task5`395ec54`;Task6`6c70f17`;Task7`8a4c49c`;Task8`bbd7851`;Task9`2608b76`. Task10/final verification commits follow.

The first Task2 commit command accidentally continued after Ruff errors;the immediate correction and fresh passing checks are recorded in history. Subsequent commit gates use verified results. Pytest temporary storage was moved to this child after shared-directory housekeeping warnings;no foreign test data was manually changed.

## Remaining verification

Finish latest full suite,contract regeneration,whole-branch fresh review,clean-checkout quickstart,and precise final evidence/commit record. Fix important findings with regression tests. Preserve the failed model gate and missing manual accessibility/claims reviews. No public repository,push,release,deployment,model upload,paid resource or external message is authorised or performed.

Latest47-test run passed in35.85s;strict Python/TypeScript,5Vitest tests,build,and unchanged contract regeneration passed. Fresh reviewer and clean-checkout check are next.
