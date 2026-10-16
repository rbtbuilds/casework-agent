# Acceptance evidence

Updated 2026-10-16. This is a synthetic, single-operator loopback simulation. V5 requires every action, outcome, generated condition and expected completion to be correct; the historical minimum thresholds remain visible separately in reports.

| Gate | Actual Qwen3 14B v5 | Same-input fixture |
| --- | --- | --- |
| Correct actions | 30/30 | 30/30 |
| Correct outcomes | 30/30 | 30/30 |
| Generated condition fields | 180/180 | Deterministic |
| Supported model reasons | 30/30 | Deterministic |
| Authorized completions | 24/24 | 24/24 |
| Unapproved / duplicate effects | 0 / 0 | 0 / 0 |
| Human factual review | Pending | Not model evidence |

Six stale cases expect no writes and are excluded from the 24-case completion denominator. All other cases create exactly one fictional ticket and annotation. The first [model report](evidence/qwen-v5-challenge.json), [fixture comparison](evidence/fixture-v5-challenge.json), [independent raw-output audit](evidence/qwen-v5-challenge-trace-review.json) and [oracle comparison](evidence/qwen-v5-challenge-oracle-comparison.json) preserve exact source, model and input identities. All 180 fields and 30 reasons/actions are correct on first replies; no semantic retry or replacement occurred. Displayed prose is application-rendered and separately AI-reviewed.

Human factual review remains unperformed: the original broader unsupported-claims gate stays open, with null counts. A small AI-authored edge-focused challenge does not establish production prevalence, a model advantage over deterministic policy, or general safety.

Final-source checks pass Ruff, strict Pyright including tests, 151 Python tests, strict TypeScript including browser tests, eight component tests, build, unchanged contracts and four actual-service browser flows. Actual Qwen browser recovery observes zero pre-approval writes, two post-commit response losses and exactly one ticket/annotation pair. Graceful cancellation persists partial traces through the run/generation fence and propagates cancellation; the next case remains processable. A fresh final-source archive separately passes locked installation and fixture verification, explicitly skipping weights-dependent inference.

Manual screen-reader testing and a recorded walkthrough remain pending. There is no public authentication, tenant isolation, cross-service rollback, distributed exactly-once guarantee or production validation. See [evaluation](../EVALUATION.md), [state](STATE.md), [review](REVIEW-2026-10-16-V5.md) and [publication audit](PUBLICATION-AUDIT.md).
