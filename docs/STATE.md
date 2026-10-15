# Casework Agent state

Updated: 2026-10-15. Phase: implementation. Task1 verified; remaining tasks in progress.

## Verified planning facts

- The initial child contained README.md, EVALUATION.md, .gitignore and LICENSE.
- `git rev-parse --show-toplevel` and `git status --short` returned `fatal: not a git repository` in this child during planning.
- No application source, dependencies, migrations, model runtime, database or tests were created or run in this planning pass.
- The parent reported Python3.12.14 available via uv, shell Python3.14.7, Node26.7.0 and npm11.19.0. Execution must probe again; these are observations, not selected runtime evidence.
- The parent reported all reserved ports free and the heavy-model lease absent during planning. These observations expire and must be checked before execution.
- Planning documentation was checked for ASCII text, balanced fenced blocks, existing relative Markdown targets, ten task sections and a plan length within the requested 300-500 lines. These are document checks, not application verification.
- The official Qwen raw model card and MLX LM documentation/Qwen2 source were read to ground the selected default; local snapshot compatibility and measured quality remain untested.

## Planned deliverables

| Task | Status | Evidence |
| --- | --- | --- |
| 1 Typed storage and first API slice | Complete | pytest3passed; Ruff clean; strict Pyright0errors. |
| 2 Independent mock services | Complete | 5pytest tests passed including actual HTTP concurrency/CAS/drop recovery; strict Pyright and Ruff clean. |
| 3 Bounded tools and fixture baseline | Complete | 14pytest tests; real HTTP tools,scope gates,48hour boundary and manual review. |
| 4 Local-model tool adapter | Implemented; probe deferred | Typed subprocess/tool tests pass; shared lease busy. |
| 5 Proposal/approval protocol | Implemented; extended matrix pending | Exact replay/hash and stale-source tests pass. |
| 6 Write execution and recovery | Not started | None |
| 7 API/lifecycle/contracts | Not started | None |
| 8 Accessible workbench UI | Not started | None |
| 9 End-to-end failure matrix | Not started | None |
| 10 Evaluation and runbook | Not started | None |

## Acceptance gates

- Fixture integration/browser checks: not run.
- Strict Python and TypeScript checks including tests: not run; application does not exist yet.
- Crash/approval/idempotency failure matrix: not run.
- Accessibility/manual visual review: not run.
- Real-model protocol capability and evaluation: not run. Default model selected in the plan: Qwen/Qwen2.5-1.5B-Instruct through project-local MLX LM in an owned subprocess. No weights downloaded, dependencies installed or model revision resolved yet; execution must pin/hash the public snapshot and probe compatibility under the resource lease.
- Human review of model claims: not run.
- Public repository, push, release, deployment and external communications: not authorized or performed.

## Next action

Matthew can paste CHAT-HANDOFF.md's execution prompt into the assigned fork. The executor reads the absolute inputs, proves its workdir, inspects Git/runtime/process reality and begins Task 1 under native superpowers:executing-plans.

The optional human contribution is 5-10 lines of delivery-exception policy or internal-note preferences. The SPEC's conservative defaults permit implementation without it. Real-model acceptance uses the selected public Qwen checkpoint and local MLX LM, with explicit snapshot download and load/unload inside the shared lease. No model/server configuration is required from Matthew.

## Execution record

Task1: Python3.12.14, feature branch feat/casework-agent-v1. Storage reopen/hash/health tests passed. Model weights absent. Initial shared pytest housekeeping warnings resolved by project-local --basetemp; foreign files left alone.

Task2: Three independent mock processes/SQLite databases verified. Dropped response uses original content length so the real HTTP client observes transport loss,not a valid short body. Concurrent same-key tickets produce one persisted effect; replay precedes annotation CAS.

Task2 check correction: the first commit command continued after Ruff reported import ordering and blocking test-process startup. Both were fixed immediately; the fresh run passed5tests,Ruff,and strict Pyright. Later commit gates use set -e.

Task3: Strict policy,scope and fixture adapter verified against real services. No write capability is exposed to either agent.

Task4: Public Qwen revision989aa7980e4cf806f80c7fef2b1adb7bc71aa306 downloaded,9 files hashed in ignored .runtime/models/snapshot.json. Probe returned model_busy without loading.16 prior tests plus2 approval tests passed; Ruff/strict Pyright clean.
Task5: Immutable proposals,transactional exact approvals,replay,and stale invalidation implemented;18tests passed. Extended expiry/cancellation matrix follows in Task9.

Task6:20tests passed before API expansion. Dropped ticket response reconciles to exactly1ticket/1annotation; cancellation before claim prevents writes; second live worker is fenced. Remaining crash/expiry matrix follows Task9.
Task7:22pytest tests passed including full process HTTP create/gather/approve/complete/replay,Origin403 and error422,occupied-port refusal. Strict Pyright0errors,Ruff clean. Worker runs as an owned task in the single API process with a durable database lease and5s heartbeat.

Task7 follow-up: Node26.7 local exception tested with Vite8.3.4/React19.3.1; CI will useNode24. TypeScript5.9.3 pinned after latest TypeScript broke openapi-typescript7.13.0. Generated OpenAPI/TS and runtime JSON-schema validation implemented. Foreground dev run added for browser ownership; detached start retains verified PID/start/argv/nonce records.15expanded crash/approval/recovery tests passed.

Task8: Workbench implemented and visually inspected at1440px light and375px dark. Vitest5component tests pass;strict TypeScript and production build pass. Exact note/hash/versions/expiry are visible; pending controls disable writes. Inbox polling was corrected after visual review showed a stale queue state.
Task9: Actual browser flow passed with both ticket and annotation response drops,exact approval replay,changed-body409,keyboard approval,zero Axe findings in tested light/dark/mobile states,and no page errors. Four real screenshots saved under .runtime/evidence.15expanded Python matrix cases passed,including restart,partial conflict,outage and worker fencing. Manual screen-reader testing remains unperformed.
Task10: Frozen fixture holdout report30/30actions,30/30workflow,24/24authorized completions;0unapproved/duplicate effects. Qwen runtime loaded and generated, but smoke JSON omitted arguments and failed schema. Full frozen Qwen benchmark is running; do not treat fixture results as model quality.
