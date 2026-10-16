# Acceptance record

Updated 2026-10-16. Verification covers a loopback, single-operator simulation with synthetic business data. The current v4 numerical results are below. The original broader zero-unsupported-claims gate remains unclaimed; intermediate model assertions and required human review are separate from application-generated explanations.

| Gate | Actual Qwen3 14B v4 | Same-input fixture |
| --- | --- | --- |
| Correct actions, target 27/30 | 29/30 | 30/30 |
| Correct final outcomes, target 27/30 | 29/30 | 30/30 |
| Authorised completions, target 22/24 | 23/24 | 24/24 |
| Unapproved writes / duplicate effects | 0 / 0 | 0 / 0 |
| Broader factual-claim gate | Unmet: known intermediate errors; human review pending | Not model inference |

The first [v4 model report](evidence/qwen-v4-challenge.json) and [fixture comparison](evidence/fixture-v4-challenge.json) identify clean source `ca3141346360a17ff9fe9cd9ceaedd6963265f7d` and manifest `16ee477fe41fa9aeb0ffc3bb66c7e119d3ca000a845a73f1fb00fc62388a221c`. Six stale cases expect no writes and are excluded from the 24-case completion denominator. All family counts and failures remain in the reports.

The fresh run retains 2 incorrect intermediate assessment fields across 2 attempts and 2 unsupported selected reasons. These are recorded in trace diagnostics and cannot change displayed explanations or authorise writes. Human review remains pending; the broader zero-unsupported-claims gate is not claimed. Code independently writes displayed explanations from evidence; this is not certification of Qwen's reasoning. [Model-assisted trace review](REVIEW-2026-10-16.md#frozen-v4-trace-review) and the human factual gate remain separate.

The original 14B v3 measurement stays at 28/30 actions and outcomes and 22/24 completions. It retained two blocked age errors, false assessment fields and incorrect explanations; its reports and [review](REVIEW-2026-10-16.md#frozen-v3-trace-review) remain unchanged.

The original 1.5B run remains 0/30 actions and 0/24 completions. The independently frozen 4B v2 run remains 17/30 actions/outcomes and 14/24 completions. Their reports and input bytes are preserved; these different sets do not form a controlled model-only comparison. Development checks, including the initial 14B 12/16 failure, remain calibration evidence.

Software verification includes 137 Python tests, eight component tests, Ruff, strict Pyright, strict TypeScript including tests, the production build and four actual-service browser flows. The opt-in Qwen browser flow uses actual inference, observes zero writes before exact approval, drops both post-commit responses and confirms one ticket/annotation pair through journals. It checks two uncertain-outcome events, one send per operation and no browser errors. Fixture CI downloads no weights; actual model evidence is separate.

Fresh archive verification passed locked installation, all strict checks, 137 Python tests, eight component tests, build, contract regeneration and three fixture browser flows, with the optional model test explicitly skipped. Actual inference was verified separately.

The failure matrix covers restart boundaries, stale approval, cancellation, competing workers, same-key retries, ambiguous writes and partial conflicts. UTC conversion limits fail one gathering cleanly and leave the same worker able to process its next case. These are bounded tests, not a distributed exactly-once guarantee.

Automated accessibility covers desktop/mobile, both themes, keyboard approval and reduced motion, with zero Axe findings in the tested states. Manual screen-reader testing and a recorded walkthrough remain unperformed. There is no public authentication, tenant isolation, cross-service rollback, production deployment or measured customer saving. See [STATE](STATE.md), [evaluation](../EVALUATION.md) and the [publication audit](PUBLICATION-AUDIT.md).
