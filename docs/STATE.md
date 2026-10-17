# Verification state

Updated 2026-10-17. Casework Agent is a synthetic, single-operator loopback application.

## Portfolio presentation and retained-evidence audit

The new [retained-evidence audit](EVIDENCE-AUDIT-2026-10-17.md) covers all 83 existing v5 attempts. Frozen independent trace checks again find 498/498 correct condition answers, 83/83 supported reasons/actions, 830 requests and zero trace issues or syntax repairs. The challenge's pre-sealed integer oracles independently agree on all 180 challenge fields. New read-only database exports bind observed payloads, proposal hashes, exact approvals, saved request bodies/keys, remote journals and actual effects: 71 approved ticket/annotation pairs and 12 stale zero-effect cases. These are consistency checks of retained artifacts, not a new unseen evaluation or proof of historical database authenticity.

The separate [AI-assisted semantic ledger](evidence/v5-semantic-review-2026-10-17.json) finds no unsupported factual statement in the 83 rendered rationales/prospective notes. It does not fill human fields: actual-model `unsupported_claims` remains null, `claims_review_complete` false and `claims_review` false. Supported, unsupported and uncertain conclusions are reported separately. The fixed-policy validator already knows the permitted answer; the demonstration establishes guarded workflow execution and recovery.

The [main recording](media/casework-qwen.mp4) is **41.60 seconds and uses actual Qwen inference**; the [separate recovery clip](media/casework-recovery.mp4) is **29.44 seconds with a fixture decision and real HTTP services**. Both use clean committed capture source `7a4bc9c`, no retries and the exposed `dev-delay-01` example. The main capture retains ten model requests and six correct conditions. Both verify zero remote effects/journals before exact browser approval, then one confirmed ticket/annotation pair and one send per operation. Recovery retains both post-commit uncertainty events; the camera explicitly brings them into view. Original uncut WebM footage, captioned MP4s, hashes and raw browser assertions are public. [Recording provenance and reproduction](WALKTHROUGH.md).

No application, model, policy, prompt or decoder behavior changed. All **359 original application/fixture/evidence files** checked against `27c81cf` remain byte-identical. New code is audit/recording tooling and its tests. A recording regression first failed because the final uncertainty event was outside the viewport; the scroll correction passed the final capture. Independent review then found inferred caption offsets lagging the UI and full-page screenshots resizing the last frames. The corrected captures use permanent mode labels and a viewport-only screenshot; regressions first failed, then passed. The [explicit correction record](evidence/presentation-media-correction-2026-10-17.json) preserves superseded media provenance. Earlier local media trials remain ignored and are not passed off as new evaluation evidence.

Current full verification passes **165 Python tests**, Ruff, strict Pyright including tests, strict TypeScript including browser/recording files, **eight component tests**, build, unchanged contract regeneration and **all four actual-service browser flows including Qwen**. The two recording flows also pass separately. No requested automated suite was skipped. The historical clean-archive results below remain at their original source and counts; no new clean-archive measurement is claimed.

The reported earlier 107-unit-pass/startup failure was a reserved-port collision with the live demo on 8212. This audit verified all five recorded process identities, stopped them through `scripts/dev.py`, ran port-owning suites sequentially and included the startup/failure tests in full pytest. All four original stopped database hashes matched before restoration. Human factual review and manual screen-reader testing remain unperformed.

The lifecycle helper has restored the original demo with its two existing cases. API and web both returned HTTP 200, model/fixture availability is true, and the shared ML lease is released. No original database was reset or replaced.

A final public GitHub check confirmed MP4 file pages do not contain an inline player. The README therefore includes an animated preview and explicit MP4 download links; the source recordings are unchanged. [Preview provenance](evidence/github-preview-2026-10-17.json).

Exact commands, log hashes, source boundaries and restoration evidence are recorded in [the dated verification artifact](evidence/presentation-final-verification-2026-10-17.json). Public asset and metadata checks are recorded in [the publication audit](PUBLICATION-AUDIT.md).

## First frozen v5 measurement

At clean source `7fe90b2657e5b8d42a655b5239d552ac65d58759`, the first actual Qwen run passed **30/30 actions and expected outcomes**, **180/180 generated condition fields**, **30/30 supported selected reasons** and **24/24 authorized completions**. Six stale cases correctly produced no writes. Unapproved and duplicate effects were zero; no syntax repairs, semantic retries or replacement answers occurred. The [same-input fixture](evidence/fixture-v5-challenge.json) passed 30/30 and 24/24 at the same clean source.

The [108-file freeze](evidence/qwen-v5-freeze.json) preceded coordinator opening. All 31 scenario/manifest files were promoted unchanged. Separate AI authorship, independent integer UTC oracles, one disclosed static runner-join replacement before sealing, original labels/inputs, compatibility checks and all hashes are retained. All 30 share coarse policy shapes with prior inputs; no statistical independence is claimed. Published cases are now exposed inputs and cannot be reused as unseen tests.

The [raw-output audit](evidence/qwen-v5-challenge-trace-review.json), [pre-authored oracle comparison](evidence/qwen-v5-challenge-oracle-comparison.json) and separate [AI-assisted review](REVIEW-2026-10-16-V5.md) agree on every generated field, reason and action, all 300 requests, and all 30 evidence-rendered rationales/notes. Human factual review remains pending: unsupported claims are null and the human gate remains false.

## Model protocol and development

Qwen selects three scoped reads, evaluates six conditions in fresh contexts containing only their rules/relevant data, then selects action/reason from its six unchanged outputs and actual observation IDs. Both Booleans, both actions and every reason remain possible. Code independently validates claims, action, citations and source revisions after generation, then renders prospective prose from raw facts. Wrong semantic output fails once without feedback, correction or fixture substitution.

Exact integer age margins and UTC relations are supplied features. The validator already knows the permitted fixed-policy action; these results demonstrate guarded inference and workflow execution, not an advantage over deterministic policy.

At clean source `4824505`, all [53 exposed development cases](evidence/qwen-v5-development.json) passed 53/53 actions/outcomes, 318/318 fields, 53/53 reasons and 47/47 completions, with zero unapproved/duplicate effects. Independent recomputation agrees; the fixture comparison is separate. Captured-input probes and a paired old/new replay remain separately labelled development evidence, not unseen or workflow measurements.

## Final source verification

After measurement, source review identified normal worker cancellation bypassing partial-trace persistence. Source `3cec490d24b9ad9287ea8b19a3d0b32a67cb5e3e` fixes only workflow cancellation handling and adds two failing-then-passing real-HTTP regressions. Available traces persist through the existing run/generation/live-lease guard, cancellation propagates, zero writes occur and the next case remains processable. Model inputs, prompts, schemas, policy, renderer, evaluation and the success path are unchanged. [Post-measurement verification](evidence/qwen-v5-postmeasurement-verification.json) records exact hashes and the two-file source delta; frozen reports remain unchanged.

Final checks pass Ruff, strict Pyright including tests, **151 Python tests**, strict TypeScript including browser/test files, **eight component tests**, production build and unchanged contract regeneration. All **four native browser flows** pass, including [actual Qwen](evidence/qwen-v5-runtime-browser.json), zero writes before approval, both post-commit response drops and one recovered ticket/annotation pair. The [final source archive](evidence/qwen-v5-runtime-clean-checkout.json) separately passes all 11 commands with locked dependencies, 151 Python tests, eight component tests and three fixture browser flows; its optional model test is explicitly skipped.

The broader failure matrix covers stale authority, cancellation, competing workers, same-key retries, ambiguous writes, restart boundaries and partial conflicts. Exact `inference_calls` retain actual request boundaries and partial errors; read `exchange` is explicitly limited to read history. Interrupted requests make aggregate token usage unknown. Hard termination cannot persist in-memory responses; restart fails interrupted gathering safely.

## Historical evidence and operating limits

Original 1.5B 0/30, v2 4B 17/30, v3 14B 28/30 and v4 29/30 reports remain unchanged, including age, chronology and intermediate-claim failures. Different inputs/protocols prevent a controlled model-size comparison. All 230 pre-v5 scenario/manifest/evidence assets are preserved.

The pinned snapshot is `mlx-community/Qwen3-14B-4bit`, revision `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`, snapshot hash `ca031ea5eef9f3c42f3bf3ee438491f53b326a41d31bde3289d931fef194355d`. Runtime measurements use Python 3.12.14, MLX LM 0.32.0, MLX 0.32.4, Outlines 1.3.3 and Apple M5 Pro/24 GiB, with temperature zero and non-thinking rendering. Node 26.7.0 is the verified local exception; CI targets Python 3.12/Node 24 without weights.

The existing developer stack was stopped through ownership checks for sequential process tests; its databases are preserved. Use `scripts/dev.py status` for current ownership rather than archived process IDs. The standard lifecycle helper restored the existing stack after verification, preserving its databases; API and web readiness both returned HTTP 200 and the model compatibility probe remains available. Weights, databases, private runtime state and credentials remain ignored. See the bounded [publication audit](PUBLICATION-AUDIT.md).

Manual human factual review and screen-reader testing remain pending. The recorded walkthrough is complete, with modes and evidence linked above. No public authentication, tenant isolation, production validation, measured customer saving, cross-service rollback or distributed exactly-once guarantee is claimed. See [evaluation](../EVALUATION.md), [configuration](MODEL-CONFIG.md) and [runbook](RUNBOOK.md).
