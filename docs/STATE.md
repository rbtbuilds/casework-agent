# Verification state

Updated 2026-10-16. This record describes a synthetic, single-operator loopback application.

## Current v4 measurement

The first frozen actual Qwen3 14B challenge records **29/30 correct actions**, **29/30 correct final outcomes** and **23/24 authorised completions**, with 0 unapproved writes and 0 duplicate effects. The identical-input fixture records 30/30 actions/outcomes and 24/24 completions. All six stale cases require zero writes. Both runs identify clean source `ca3141346360a17ff9fe9cd9ceaedd6963265f7d`; the 104 runtime/test/configuration files match the implementation freeze at `b7cd022`.

Qwen selects its action after scoped reads and structured intermediate generation. The context supplies exact integer age margins and computed UTC relations. Code independently validates policy, scope, citations and hashes, then derives a prospective explanation and note from raw evidence. A wrong action fails without correction, feedback or fixture fallback. Intermediate assertions have no authority over displayed text or writes. The remaining fresh-set failure is a timezone-naive carrier event incorrectly treated as consistent by Qwen; policy validation blocked it before any proposal, approval or writes.

The fresh run retains 2 incorrect intermediate assessment fields across 2 attempts and 2 unsupported selected reasons. These are recorded in trace diagnostics and cannot change displayed explanations or authorise writes. Human review remains pending; the broader zero-unsupported-claims gate is not claimed. See [evaluation](../EVALUATION.md), [repair design](MODEL-REPAIR-V4.md), [model configuration](MODEL-CONFIG.md) and [trace review](REVIEW-2026-10-16.md#frozen-v4-trace-review).

## Source and split integrity

The separately authored 30-case v4 challenge stayed sealed until after calibration, source freeze and actual-model browser verification. First access and exact-byte promotion are recorded in the authorship artifact. Manifest SHA-256: `16ee477fe41fa9aeb0ffc3bb66c7e119d3ca000a845a73f1fb00fc62388a221c`. Later runs are reproductions. Case authorship was by a separate AI agent, not a human or external benchmark provider.

All 23 exposed development cases passed final actual inference at clean source `9f9b245`. Both original age failures now select manual review and display the exact below-threshold values. Two intermediate carrier-check assertions and reasons remained wrong. Earlier strict-validation runs remain frozen at 18/23, 22/23 and 20/23; the rejected action-only replay remains 4/7. No failed workflow was retroactively credited.

## Software verification

Ruff, strict Pyright including tests, all 137 Python tests, strict TypeScript including test/browser files, eight component tests, production build and byte-identical contract regeneration passed. A [fresh source archive](evidence/qwen-v4-clean-checkout.json) passed all 11 recorded commands with locked installation, 137 Python tests, eight component tests and three fixture browser flows; its model test was explicitly skipped.

All four native actual-service browser flows passed at clean source `b7cd022`, including actual Qwen inference. The [browser evidence](evidence/qwen-v4-browser.json) records zero writes before approval, two post-commit response losses, one confirmed ticket/annotation pair, one send per operation and zero browser errors. Screenshot identities and coordinator attribution are explicit; the raw capture itself has no independent loaded-model identifier.

The failure matrix covers stale approval, cancellation, competing workers, same-key retries, ambiguous writes, restart boundaries and partial conflicts. The same worker continues after unrepresentable UTC timestamps. Automated accessibility covers both themes, desktop/mobile layouts, keyboard approval and reduced motion; screen-reader testing and a recorded walkthrough remain unperformed.

## Historical results and limits

Original 1.5B 0/30, 4B v2 17/30 and 14B v3 28/30 results remain unchanged. V3 also retained two blocked age errors and incorrect generated explanations. Different inputs and protocols prevent a controlled model-only comparison.

The pinned snapshot is `mlx-community/Qwen3-14B-4bit` at revision `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`, with explicit non-thinking rendering, temperature zero and constrained JSON generation. Measurements used Python 3.12.14, MLX LM 0.32.0, MLX 0.32.4 and Outlines 1.3.3 on an Apple M5 Pro with 24 GiB memory. Node 26.7.0 is the supported local exception; CI targets Python 3.12 and Node 24 on Ubuntu without weights. Current [GitHub Actions](https://github.com/rbtbuilds/casework-agent/actions/workflows/ci.yml) must identify their own source.

No public authentication, tenant isolation, production validation, customer time-saving measurement, cross-service rollback or distributed exactly-once guarantee is claimed. Weights, databases, private runtime state and secrets remain ignored. Model and data terms are separate from the MIT source licence. See the bounded [publication audit](PUBLICATION-AUDIT.md).
