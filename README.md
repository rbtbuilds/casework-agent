# Casework Agent

[![Fixture verification](https://github.com/rbtbuilds/casework-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/rbtbuilds/casework-agent/actions/workflows/ci.yml)

A local Qwen agent for delivery exceptions, with exact human approval and durable HTTP writes. Built with FastAPI, React, TypeScript and SQLite. The model reads order and carrier evidence, proposes an internal action and waits for approval. A fenced worker recovers uncertain ticket and annotation writes through remote journals. All business records are synthetic.

**Actual-model result:** 28/30 correct workflows and 22/24 authorised completions on a fresh synthetic challenge. Two threshold errors stopped before writes; factual review remains open. [Full evaluation](EVALUATION.md).

![Actual local Qwen proposal awaiting exact approval](docs/evidence/qwen-v3-proposal.png)

## Run the model

Requirements: Python 3.12, uv and Node.js 24 LTS. Local inference requires macOS on Apple Silicon. The pinned Qwen3 14B 4-bit checkpoint downloads approximately 8.3 GB of weights and needs no cloud credentials.

```sh
git clone https://github.com/rbtbuilds/casework-agent.git
cd casework-agent
uv sync --locked --extra model
npm --prefix web ci
uv run --no-sync python scripts/model_session.py prepare
uv run --no-sync python scripts/model_session.py probe
uv run --no-sync python scripts/dev.py start
# Open http://127.0.0.1:5112
```

Select **Local Qwen model**, open the delayed delivery example and inspect the source records, rationale and exact note. Approve the fictional action; the final view shows a confirmed ticket and order annotation. Use `uv run --no-sync python scripts/dev.py stop` to stop the owned services.

For the deterministic workflow without weights, install with `uv sync --locked` and select **Fixture workflow**. That path runs on macOS and Ubuntu CI. Modes remain visibly labelled; a model failure never substitutes a fixture decision. The [runbook](docs/RUNBOOK.md) covers both setups and preserves existing demo databases.

## Approval and recovery

```mermaid
flowchart LR
  UI[Operator workbench] --> API[FastAPI and SQLite]
  API --> Reads[Scoped order, carrier and policy reads]
  Reads --> Qwen[Qwen with constrained JSON]
  Qwen --> Validation[Independent policy and evidence validation]
  Validation --> Proposal[Immutable proposal]
  Proposal --> Approval[Exact operator approval]
  Approval --> Worker[Fenced durable worker]
  Worker --> Services[Ticket and order HTTP services]
  Services --> Journal[Same-key journal reconciliation]
  Journal --> Worker
```

The decoder permits scoped read tools and actual citation IDs. Qwen generates a six-condition assessment, chooses the action and drafts the note; deterministic code checks its decision without giving policy-answer feedback. Approval binds the exact proposal hash, evidence versions, policy and expiry.

Before every write, the worker saves its key, body and hash. A lost response remains unknown until the matching remote journal confirms it. Replays preserve the same payload and key within a three-send budget. A ticket followed by an annotation conflict remains a visible partial result; no rollback is fabricated.

## Measured model workflow

The first frozen v3 challenge used 30 new synthetic cases, including six stale approvals that must produce no writes. The fixture and Qwen runs used identical inputs and fault schedules.

| Metric | Actual Qwen3 14B | Fixture |
| --- | --- | --- |
| Correct actions | 28/30 | 30/30 |
| Correct final outcomes | 28/30 | 30/30 |
| Authorised completions | 22/24 | 24/24 |
| Unapproved / duplicate effects | 0 / 0 | 0 / 0 |

These clear the action, workflow and completion targets of 27/30, 27/30 and 22/24. Human review of factual claims remains pending, so full model acceptance is open. Warm workflow p50 was 35.04 seconds and p95 54.50 seconds on an Apple M5 Pro with 24 GiB memory; loading is recorded separately. The small synthetic set is not an industrial benchmark. [Reports, per-case traces and reproduction](EVALUATION.md) identify the exact source and model snapshots.

Two below-threshold generations falsely claimed that the event age met 48 hours. Exact policy validation rejected both before proposal publication, approval or writes. Their traces retain the one-second and one-microsecond shortfalls. A model-assisted trace review also found three incorrect assessment fields among correct decisions, two incorrect rationales, two premature escalation notes and one imprecise timestamp note. These findings are detailed in [the source and trace review](docs/REVIEW-2026-10-16.md). Human factual review remains pending; action accuracy does not certify explanation accuracy.

## Evaluation history

The original Qwen2.5 1.5B run produced 0/30 valid actions. A constrained Qwen3 4B iteration reached 29/30 on development cases, then 17/30 on a separately authored challenge, with 14/24 authorised completions. The failed runs remain available with source, model and input hashes. They used different case sets; their scores are not a controlled model-only comparison.

## Verification

A [fresh archive verification](docs/evidence/qwen-v3-clean-checkout.json) passed locked installation, 94 Python tests, eight component tests, strict checks, build, contract regeneration and three fixture browser flows. The model test was explicitly skipped there and exercised separately with actual inference.

The complete software checks include 94 Python tests, eight component tests, strict Python and TypeScript checks, a production build and four real-service browser flows. The actual-model browser flow verifies zero writes before approval, both post-commit response drops, and one recovered ticket/annotation pair. CI runs fixture verification without weights; actual inference is a separate opt-in check.

```sh
uv run --no-sync ruff check .
uv run --no-sync pyright
uv run --no-sync pytest -q
npm --prefix web run typecheck
npm --prefix web test -- --run
npm --prefix web run build
PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e
# With the pinned model prepared and the shared lease available:
CASEWORK_REAL_MODEL=1 PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e
```

Install Chromium as described in the runbook before the first browser check. Stop the demo first and run port-owning suites sequentially. Tested accessibility covers keyboard approval, reduced motion, both themes and desktop/mobile layouts with zero Axe findings in those states. Manual screen-reader testing remains unperformed.

The application is a single-operator loopback simulation. It has no public authentication, cross-service rollback or distributed exactly-once guarantee. Human review of generated factual claims remains pending; passing action checks does not certify free-text accuracy. No production deployment or customer time saving is claimed.

See [evaluation](EVALUATION.md), [model configuration](docs/MODEL-CONFIG.md), [engineering decisions](docs/ENGINEERING-DECISIONS.md), [verification state](docs/STATE.md) and the [case study](docs/CASE-STUDY.md). Contribution and reporting guidance are in [CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md). Code and original fixtures are [MIT licensed](LICENSE); model assets retain separate terms and weights are excluded from Git.
