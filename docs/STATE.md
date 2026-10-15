# Casework Agent state

Updated 2026-10-16. Repository: [rbtbuilds/casework-agent](https://github.com/rbtbuilds/casework-agent).

## Current implementation checkpoint

The model path uses pinned `mlx-community/Qwen3-14B-4bit`, revision `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`, with MLX LM and Outlines. Qwen generates six policy-assessment booleans, chooses its action and drafts the note. The decoder leaves both boolean values and both actions available. Deterministic policy validation rejects an incorrect decision without feedback or another choice. Fixture mode remains explicit and separate.

All **94 Python tests**, **eight component tests**, Ruff, strict Pyright, strict TypeScript including browser tests, and the production build pass. Regenerating the three API contract artifacts reproduced their bytes. The full Python suite passed in 49.30 seconds. Port-owning suites ran sequentially.

Commands: `uv run --no-sync ruff check .`; `uv run --no-sync pyright`; `uv run --no-sync pytest -q`; `npm --prefix web run typecheck`; `npm --prefix web test -- --run`; `npm --prefix web run build`; `uv run --no-sync python scripts/export_contracts.py`; `npm --prefix web run contracts`. Browser and fresh-challenge execution remain pending for this checkpoint.

The protocol probe succeeded for the pinned 14B snapshot. The first 14B development run passed only 12/16; the explicit-assessment protocol then passed **16/16 actions and workflows**, with zero unapproved or duplicate effects. Both reports remain calibration evidence with their actual dirty source states and prompt hashes. See [MODEL-ITERATION](MODEL-ITERATION.md) and the [development report](evidence/qwen-v3-development.json).

The source review closed the replayed-delimiter and UTC-overflow findings. Regressions prove that invalid UTC case clocks return HTTP 422 without creating a case, an unnormalizable carrier event fails gathering without operations, and the same worker handles its next case. The [review record](REVIEW-2026-10-16.md) distinguishes source inspection from execution evidence.

## Evaluation boundary

The original 1.5B report remains **0/30** actions and **0/24** completions. The independently frozen 4B v2 report remains **17/30** actions/workflows and **14/24** completions; all 13 incorrect proposals stopped before writes. The same-input v2 fixture passed 30/30 workflows and 24/24 completions. These reports and their inputs are unchanged.

The independently authored v3 challenge remains private and unopened by the implementer at this source checkpoint. Its manifest SHA-256 is `a51c64475b1a5081b60b117d78a961e248f35b2edf7749b7ff56868ab9870e4c`. It will be promoted unchanged after the implementation freeze, then measured once on clean committed source. No v3 challenge result or model acceptance is claimed here.

## Runtime and publication

Python 3.12.14, MLX LM 0.32.0, MLX 0.32.4 and Outlines 1.3.3 run on Apple M5 Pro hardware with 24 GiB memory. Node 26.7.0 is the supported local exception; CI targets Python 3.12 and Node 24 on Ubuntu. Fixture CI downloads no weights. Model execution uses an offline owned child under the shared machine lease, with exit confirmed before release.

No source push has occurred during this repair; public main remains `d8956e0`. The publication audit found no active credentials, customer records, weights, databases or unrelated source in its inspected scope. Historical workstation paths and obsolete cleanup markers remain documented. New exports redact runtime paths and ownership metadata while preserving measurements and identifying raw report hashes. See [PUBLICATION-AUDIT](PUBLICATION-AUDIT.md).

Human factual-claim review, manual screen-reader testing and a recorded walkthrough remain unperformed. Assessments and generated prose remain model claims. The application is a loopback, single-operator simulation without public authentication, tenant isolation, cross-service rollback or production validation.

The developer stack was stopped through its ownership-checked helper for tests. Its original databases are preserved; restore it after final verification. No model weights, private runtime state or unrelated files belong in a source push.
