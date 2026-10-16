# Verification state

Updated 2026-10-16. Active v5 repair on `fix/model-condition-reasoning`; first fresh measurement complete. Graceful-shutdown trace persistence is being repaired separately after this frozen run.

## First frozen v5 result

At clean source `7fe90b2657e5b8d42a655b5239d552ac65d58759`, the first 30-case actual Qwen run produced 30/30 actions/outcomes, 180/180 correct generated fields, 30/30 supported reasons and 24/24 authorized completions. Six stale cases correctly produced no writes. Unapproved and duplicate effects were both zero; no syntax or semantic retries occurred. The same-input fixture also passed 30/30 and 24/24 at the same clean source. The independent trace audit and pre-authored civil-calendar integer UTC oracles agree on every generated field and decision. Human factual review remains false/null.

The 108-file implementation freeze and trace auditor preceded coordinator opening. All 31 promoted scenario/manifest files match the private originals. The author independently created literal cases and initial labels, with one documented static runner-join replacement before typed verification and sealing; original bytes and labels remain preserved. No target-model outcomes informed authoring. Authorship is by a separate AI agent, not a human, and all cases share coarse policy shapes with prior inputs. After publication, these cases are exposed inputs, not a reusable unseen test.


## Verified v5 development

At clean source `482450554abcde7c08dde0487e110a32b49080cd`, actual Qwen passed all 53 exposed cases: 53/53 actions and expected outcomes, 47/47 authorized completions, 318/318 generated fields and 53/53 supported reasons. There were zero unapproved/duplicate effects and no syntax repairs. The independently implemented trace audit agrees with every generated field, raw action and reason, with zero trace issues. The same-input fixture comparison also passed 53/53 and 47/47 at the same clean source. These inputs are development-only, including all published v4 cases; the fresh measurement is recorded above.

The staged protocol generates six conditions in isolated contexts and then chooses action/reason from those unchanged outputs. Independent validation rejects false claims and unsupported reasons before proposal publication. Exact request boundaries, schemas, replies and partial failures are retained. Review closed three reporting gaps: strict all-case gates, unknown usage after interrupted inference, and post-attempt scoring of partial condition outputs. Ten adversarial report mutations verified the separate auditor.

Ruff, strict Pyright including tests, strict TypeScript, all 149 Python tests, eight component tests, build and unchanged contracts pass. Four actual-service browser flows pass, including real Qwen, exact approval and both dropped-response recoveries. A fresh source archive passed all 11 recorded commands: locked installation, strict checks, 149 Python tests, eight component tests, build, unchanged contract regeneration and three fixture browser flows. Its optional model test was explicitly skipped; actual-model browser inference was verified separately. The existing developer stack was ownership-checked and stopped for sequential process tests; its databases are preserved for restoration.

Exposed captured-input probes remain separate from workflow measurements: nine cases (54/54 fields), two true-conflict controls (12/12), and a paired four-case replay reproducing both v4 errors while isolated requests answered correctly. Curated raw requests/replies and script snapshots are committed under `docs/evidence/v5-development-probes`. Human factual review, screen-reader testing and a recorded walkthrough remain pending.

Updated 2026-10-16. This record describes a synthetic, single-operator loopback application.

## Historical v4 measurement

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
