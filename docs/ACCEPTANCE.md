# Acceptance record

Updated 2026-10-16. Verification covers a loopback, single-operator simulation with synthetic business data. V3 clears the numerical model-action and workflow gates; full model acceptance remains open pending human review of every generated factual claim, including the assessment booleans.

| Gate | Actual Qwen3 14B | Same-input fixture |
| --- | --- | --- |
| Correct actions, target 27/30 | 28/30 | 30/30 |
| Correct final outcomes, target 27/30 | 28/30 | 30/30 |
| Authorised completions, target 22/24 | 22/24 | 24/24 |
| Unapproved writes / duplicate effects | 0 / 0 | 0 / 0 |
| Human factual-claim review | Pending; count is null | Not model inference |

The first [v3 model report](evidence/qwen-v3-challenge.json) and [fixture comparison](evidence/fixture-v3-challenge.json) record clean source `a79256d09cf2dc8b1e8964ec910b826a8dd1e7c1` and manifest `a51c64475b1a5081b60b117d78a961e248f35b2edf7749b7ff56868ab9870e4c`. Six stale cases expect no writes and are excluded from the 24-case completion denominator. All failures and family counts remain in the reports.

Two below-threshold generations falsely claimed that the event age met 48 hours. Exact policy validation rejected both before proposal publication, approval or writes. Their traces retain the one-second and one-microsecond shortfalls. A model-assisted trace review also found three incorrect assessment fields among correct decisions, two incorrect rationales, two premature escalation notes and one imprecise timestamp note. These findings are detailed in [the source and trace review](REVIEW-2026-10-16.md). Human factual review remains pending; action accuracy does not certify explanation accuracy.

The original 1.5B run remains 0/30 actions and 0/24 completions. The independently frozen 4B v2 run remains 17/30 actions/outcomes and 14/24 completions. Their reports and input bytes are preserved; these different sets do not form a controlled model-only comparison. Development checks, including the initial 14B 12/16 failure, remain calibration evidence.

Software verification includes 94 Python tests, eight component tests, Ruff, strict Pyright, strict TypeScript including tests, the production build and four actual-service browser flows. The opt-in Qwen browser flow uses actual inference, observes zero writes before exact approval, drops both post-commit responses and confirms one ticket/annotation pair through journals. It checks two uncertain-outcome events, one send per operation and no browser errors. Fixture CI downloads no weights; actual model evidence is separate.

Fresh archive verification passed locked installation, all strict checks, 94 Python tests, eight component tests, build, contract regeneration and three fixture browser flows, with the optional model test explicitly skipped. Actual inference was verified separately.

The failure matrix covers restart boundaries, stale approval, cancellation, competing workers, same-key retries, ambiguous writes and partial conflicts. UTC conversion limits fail one gathering cleanly and leave the same worker able to process its next case. These are bounded tests, not a distributed exactly-once guarantee.

Automated accessibility covers desktop/mobile, both themes, keyboard approval and reduced motion, with zero Axe findings in the tested states. Manual screen-reader testing and a recorded walkthrough remain unperformed. There is no public authentication, tenant isolation, cross-service rollback, production deployment or measured customer saving. See [STATE](STATE.md), [evaluation](../EVALUATION.md) and the [publication audit](PUBLICATION-AUDIT.md).
