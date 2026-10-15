# Casework Agent state

Updated: 2026-10-15. Phase: planning only. Implementation: not started.

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
| 1 Typed storage and first API slice | Not started | None |
| 2 Independent mock services | Not started | None |
| 3 Bounded tools and fixture baseline | Not started | None |
| 4 Local-model tool adapter | Not started | None |
| 5 Proposal/approval protocol | Not started | None |
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
