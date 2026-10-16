# Casework Agent state

Updated 2026-10-16. Repository: [rbtbuilds/casework-agent](https://github.com/rbtbuilds/casework-agent).

## V4 repair in progress

The internal v4 protocol adds exact policy-relative age arithmetic, checks every model assessment and primary reason, and renders bounded prospective explanations from validated facts. Qwen still chooses its assessments, reason and action; the application writes the displayed prose. See [repair design](MODEL-REPAIR-V4.md). Historical v3 results below apply only to their recorded source.

Focused regressions reproduce false-assessment publication, near-threshold precision, shared-zone daylight-saving/fold errors and an early proposal escaping worker failure handling. The implementation closes those paths. Strict checks, complete software tests, actual inference calibration and a separately authored fresh v4 challenge must finish before any new model-quality claim. The shared machine lease was busy with Evidence RAG at the first inference attempt; no model loaded and no challenge was opened.

## Verified model and workflow

Pinned `mlx-community/Qwen3-14B-4bit`, revision `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`, runs through MLX LM with explicit non-thinking chat rendering and Outlines JSON Schema decoding. Qwen generates six policy-assessment booleans, chooses its action and drafts the note. Both boolean values and both final actions remain available; the backend supplies no eligibility answer and rejects an incorrect policy decision without feedback or a second choice.

The first frozen v3 challenge at clean source `a79256d09cf2dc8b1e8964ec910b826a8dd1e7c1` produced **28/30 correct actions**, **28/30 expected final outcomes** and **22/24 authorised completions**, with **zero unapproved writes and duplicate effects**. The same-input fixture passed 30/30 and 24/24. Six intentionally stale cases require no writes. The numerical targets are 27/30, 27/30 and 22/24. Full model acceptance remains open: human review of all factual claims, including model assessment booleans, is pending and unsupported-claim counts remain null.

The runtime source froze at `3c5a2377bf759e9b8aee231a6c1fb547a115cdb4` before challenge access. Its 64 source hashes match the data-only benchmark commit. Manifest SHA-256: `a51c64475b1a5081b60b117d78a961e248f35b2edf7749b7ff56868ab9870e4c`. Inputs, manual oracles and both full reports are preserved in `fixtures/` and `docs/evidence/`. See [evaluation](../EVALUATION.md), [freeze](evidence/qwen-v3-freeze.json) and [model configuration](MODEL-CONFIG.md).

The original 1.5B 0/30 and 4B v2 17/30 failures remain unchanged. The first 14B development run passed 12/16; the explicit-assessment development run passed 16/16. Development and historical case sets are separate from the fresh v3 measurement and do not establish a controlled model-size comparison.

Two below-threshold generations falsely claimed that the event age met 48 hours. Exact policy validation rejected both before proposal publication, approval or writes. Their traces retain the one-second and one-microsecond shortfalls. A model-assisted trace review also found three incorrect assessment fields among correct decisions, two incorrect rationales, two premature escalation notes and one imprecise timestamp note. These findings are detailed in [the source and trace review](REVIEW-2026-10-16.md). Human factual review remains pending; action accuracy does not certify explanation accuracy.

## Software verification

All **94 Python tests**, **eight component tests**, Ruff, strict Pyright, strict TypeScript including test/browser files and the production build pass. All **four actual-service browser flows pass** on clean source `3c5a2377bf759e9b8aee231a6c1fb547a115cdb4`, including actual 14B Qwen inference. The model browser flow records zero writes before exact approval, two uncertain-outcome events after dropped responses, one recovered ticket/annotation pair, one send per operation and no browser errors. Browser capture and source/model attribution are preserved in [browser evidence](evidence/qwen-v3-browser.json).

A [fresh archive verification](evidence/qwen-v3-clean-checkout.json) passed all 11 commands with a new virtual environment and node_modules, including all 94 Python tests, eight component tests and three fixture browser flows. The optional model test was explicitly skipped in that weights-free environment; the separate native actual-model browser run above passed all four flows. The browser tests use a file-controlled application clock for deterministic expiry checks; fetched source timestamps and measured timings retain their own clocks.

The three generated API contract artifacts reproduce byte-for-byte. Port-owning suites ran sequentially. Commands: `uv run --no-sync ruff check .`; `uv run --no-sync pyright`; `uv run --no-sync pytest -q`; `npm --prefix web run typecheck`; `npm --prefix web test -- --run`; `npm --prefix web run build`; `uv run --no-sync python scripts/export_contracts.py`; `npm --prefix web run contracts`; `CASEWORK_REAL_MODEL=1 PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e`. The exact evaluation commands are in EVALUATION and RUNBOOK.

Regressions cover escaped incoming and replayed chat delimiters, no policy-answer repair, timestamp precision/signs, UTC admission errors, failed gathering and same-worker continuation. The complete failure matrix also covers restart, cancellation, stale authority, competing workers, ambiguous sends, same-key recovery and partial conflicts. The [source review](REVIEW-2026-10-16.md) closed its findings; source inspection and execution evidence are distinguished.

## Runtime and operating limits

Python 3.12.14, MLX LM 0.32.0, MLX 0.32.4 and Outlines 1.3.3 were measured on an Apple M5 Pro with 24 GiB memory. Node 26.7.0 is the supported local exception. CI targets Python 3.12 and Node 24 on Ubuntu and downloads no weights. Current remote checks are available in [GitHub Actions](https://github.com/rbtbuilds/casework-agent/actions/workflows/ci.yml); the model measurements above identify their own exact source.

Actual inference acquires the shared machine lease, verifies the pinned snapshot and runs in an offline owned child. The benchmark confirms child exit before releasing its lease. Fixture mode is explicit, with no fallback from model failure. The developer stack was restored after verification with the ownership-checked lifecycle helper, preserving existing databases; all five local services passed their health checks.

The publication audit found no active credentials, customer records, weights, databases or unrelated source in its inspected scope. Historical workstation paths and obsolete cleanup markers remain documented; new report exports remove runtime paths and ownership metadata while preserving measurements and raw report hashes. See [PUBLICATION-AUDIT](PUBLICATION-AUDIT.md).

Human factual-claim review, manual screen-reader testing and a recorded walkthrough remain unperformed. Automated accessibility covers desktop/mobile, both themes, keyboard approval and reduced motion. This is a loopback, single-operator simulation without public authentication, tenant isolation, cross-service rollback, production validation or measured customer savings. Future model/prompt changes require a new development iteration and fresh challenge; never retune against frozen answers.
