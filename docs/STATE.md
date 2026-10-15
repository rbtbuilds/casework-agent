# Casework Agent state

Updated: 2026-10-16. Repository: [rbtbuilds/casework-agent](https://github.com/rbtbuilds/casework-agent). The local model repair selects pinned Qwen3 4B Instruct 2507 4-bit with MLX and schema-constrained decoding. Fixture mode remains explicit and separate.

## Verified implementation checkpoint

All **83 Python tests**, **eight component tests**, Ruff, strict Pyright, strict TypeScript including browser tests, and the production build pass. All **four browser flows pass together**, including actual Qwen inference through the UI/API and both dropped-write responses. The actual-model browser check observed zero writes before approval, two uncertain-outcome events, then one confirmed ticket and one annotation, with one send per operation and no browser errors.

The three fixture browser flows also pass without model execution; the optional model test is explicitly skipped in that configuration. An earlier actual-model browser attempt returned `model_busy` while another project held the shared lease. It was interrupted and is excluded from successful inference evidence. The subsequent complete four-test run used the available lease and passed.

Commands: `uv run --no-sync ruff check .`; `uv run --no-sync pyright`; `uv run --no-sync pytest -q`; `npm --prefix web run typecheck`; `npm --prefix web test -- --run`; `npm --prefix web run build`; `CASEWORK_REAL_MODEL=1 PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e`. Python and browser process suites ran sequentially. Regenerating the three API contract artifacts reproduced their bytes; application contracts have not changed.

A separate source reviewer closed all findings, including loaded-snapshot attribution, shared browser identity/counts, external manifest metadata and binary policy-answer feedback. See [the review](REVIEW-2026-10-16.md). Wrong policy decisions now fail without feedback or another choice. A compact context copies observed fields and calculates event age without supplying an action oracle. Generated factual claims still require review.

## Model development and evaluation boundary

The original 1.5B/MLX benchmark remains frozen at source `1da911fb12bb896e750248a67f22345bf3d7892b`: **0/30 actions, 0/24 completions**, with no writes. The original fixture report records 30/30 actions and outcomes, 24/24 completions and no unapproved or duplicate effects. These are historical measurements, not current-model results.

Development comparisons selected Qwen3 after 1.5B and 7B candidates produced 2/5 and 3/5 correct actions. Qwen3 produced 5/5 in the initial comparison. After compact fact preparation, its larger development run produced **29/30** correct actions and completed workflows; the single missing-timestamp error stopped before approval or writes. The final chronology clarification then passed **6/6** development regressions, including that failure. Development reports record their actual in-progress source state and separate prompt hashes. See [the iteration record](MODEL-ITERATION.md).

At this implementation checkpoint, the separately authored 30-case challenge is frozen and **has not been opened by the implementer or evaluated**. Its manifest hash is `74a9dbbf7dbe2c6722cca29ec646cef438095dae2bc24a722c7ee9c282ecc67f`. It will be promoted unchanged after committing this model/protocol freeze. Challenge execution and its measured results remain pending at this checkpoint.

The selected model is `mlx-community/Qwen3-4B-Instruct-2507-4bit`, revision `50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b`. Preparation hashes weights, configuration, tokenizer and the separate chat template. Actual inference uses an offline owned child under the shared machine lease. The original 1.5B and comparison 7B profiles remain explicit options, with no automatic substitution. See [MODEL-CONFIG](MODEL-CONFIG.md) and [RUNBOOK](RUNBOOK.md).

## Publication and remaining limits

The published-history audit found no active credentials, weights, databases, customer records or unrelated source. Historical reports contain workstation paths and obsolete local cleanup markers; the author email already matches public profile contact information. New curated development exports remove private runtime paths and ownership metadata, preserve measurements and identify their raw source hashes. All 13 original evidence files remain unchanged. See [the bounded publication audit](PUBLICATION-AUDIT.md).

Human factual-claim review, manual screen-reader testing and a recorded walkthrough remain unperformed. The model's generated prose is not certified free of unsupported claims. Automated accessibility checks cover both themes and desktop/mobile widths in the fixture browser flow. The application remains a loopback, single-operator simulation with synthetic records, no public authentication, cross-service rollback or production validation.

Python 3.12.14, MLX LM 0.32.0, MLX 0.32.4 and Outlines 1.3.3 run on Apple M5 Pro hardware with 24 GiB memory. Node 26.7.0 is the recorded supported local exception; CI targets Python 3.12 and Node 24 on Ubuntu. The prior published source passed [CI run 38810735255](https://github.com/rbtbuilds/casework-agent/actions/runs/38810735255); a new source push must obtain its own CI result.

The developer stack was stopped through its ownership-checked lifecycle helper for tests. Its original databases are preserved; restore that stack after final verification. No model weights, private runtime state or unrelated files belong in a source push.
