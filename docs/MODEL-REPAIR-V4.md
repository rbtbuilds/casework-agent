# Grounded policy decisions and explanations

V3 met the numerical action targets but retained two wrong age comparisons, three wrong assessment fields alongside correct decisions, two incorrect rationales, premature escalation wording and an imprecise timestamp note. The original inputs, model replies and reports remain frozen. This repair changes the internal model protocol; the operator API, business policy, exact approval and durable HTTP execution stay in place.

## Current authority boundary

Qwen reads the scoped order, shipment and policy, produces a six-condition intermediate assessment and reason, and selects the action. Both boolean values, every reason and both actions remain available in the generation schema. Exact policy-relative age and generic UTC temporal relations are computed in code; this is not evidence of unaided model arithmetic or chronology reasoning. The decoder binds citations to all fetched observation IDs, so this demonstrates traceability rather than independent evidence selection.

Only the generated action and citations are accepted as decision inputs. The application independently validates policy, scope, hashes and coverage before generating any proposal text. A wrong action fails immediately without substitution, feedback, another choice or fixture fallback. Intermediate model assertions remain untrusted: their mismatched fields and reason support are recorded under `assessment_diagnostics` alongside unchanged raw replies. `decision_validated` describes the action validation, not the truth of every trace assertion.

The application derives a sufficient reason from raw observations, in a fixed display order, and `observed-policy-renderer-v3` writes the rationale and prospective note. Model assessments and reasons cannot change this text. The renderer distinguishes missing timestamps, unknown timezones and chronology faults, retains exact integer ages, and excludes arbitrary notes, descriptions and exception text. This is an application-generated policy explanation, not a claim about why Qwen chose its action.

This authority change is versioned before the fresh challenge as `casework-json-schema-v4-guarded-deliberation`. It fixes the operator-facing explanation boundary, not Qwen's incorrect intermediate assertions. The original broader zero-unsupported-claims gate is unchanged and remains unavailable when trace assertions are false or human review is missing. Rendered-output review and intermediate discrepancies must be reported separately. The deterministic validator already knows the permitted action; these measurements do not prove that the model improves decision quality over code for this fixed policy.

All temporal comparisons normalise aware datetimes to UTC before subtraction or ordering. Unknown timezones remain unknown. UTC conversion failures stop model gathering safely; the deterministic policy conservatively selects manual review for unrepresentable clocks. Regressions cover spring daylight-saving differences and ambiguous autumn scans using shared timezone objects.

## Verification and evaluation procedure

1. Reproduce false assessments and explanations; preserve the strict-validation experiments and failures. Validate the consequential model choice and isolate intermediate assertions from displayed text.
2. Exercise threshold distances below, equal to and above zero, every exclusion, absent/naive clocks, UTC bounds, early proposals, scope errors, hostile text and bounded prospective explanations.
3. Run strict Python and TypeScript checks, complete software tests, contract reproduction and actual-service browser recovery. Model inference uses the shared machine lease; fixture checks remain separate.
4. Calibrate on `fixtures/manifests/v4-development.json`. Its 23 exposed regression cases include 16 earlier development inputs and seven previously published v3 cases. These are not unseen evaluation.
5. Freeze implementation, prompt, schema and model identities before opening the separately authored v4 challenge. Promote the author's exact input bytes, record the first run and compare the same-input fixture workflow. Any later rerun is reproduction or diagnostics.
6. Review all model choices and rendered explanations against observations. Model-assisted review does not satisfy the required human review. Keep known failures and pending review visible in the public acceptance record.

The selected model remains the pinned Qwen3 14B checkpoint recorded in [MODEL-CONFIG](MODEL-CONFIG.md). New measurements and their source commits belong in [STATE](STATE.md) and [EVALUATION](../EVALUATION.md). Historical scores are not a controlled model-only comparison.

## Development finding: condition grouping

The first v4 calibration at `1631ede` accepted 18/23 cases. Every age-boundary case passed, but five assessment mismatches were blocked. Four involved chronology; three of those also incorrectly labelled a timestamp fault as a carrier conflict. Another overstated the shipment-status check. The [failed report](evidence/qwen-v4-initial-development.json) remains unchanged.

The next experiment replaces the flat computed-facts block with six `CHECK_INPUTS` groups keyed by the assessment fields. Conflict input contains only the recorded flag and normalized codes; chronology contains every UTC timestamp and signed offset in source order, without statuses, codes or the age threshold. Grouping is organizational guidance inside one prompt, not a separate security boundary. It supplies no predicate outcomes and changes neither the response choices nor semantic validation. The entire same exposed development set is used for comparison.

## Development finding: explicit temporal comparison

Grouping at `fc922f4` accepted 22/23 cases. The remaining newer-scan case still claimed consistent chronology despite a negative event-to-summary difference. The [complete grouped report](evidence/qwen-v4-grouped-development.json) preserves that failure. The next change supplies generic UTC pairwise relations (`before`, `equal`, `after`, `unknown`) for the summary against the case clock and for every event against both clocks. Every event is included in source order, including unknown times; exact timestamps and deltas remain present.

This moves temporal comparison into code. Qwen selects decisions over computed temporal features and applies the unchanged policy: an `after` or `unknown` relation fails the chronology condition. No aggregate consistency flag, expected assessment, eligible action or dataset oracle is supplied. The response schema and strict validator are unchanged. A complete repeat of the same 23 exposed cases checks the change before any fresh evaluation.

## Reason selection is not failure priority

The temporal-relation run at `1474d77` accepted 20/23 workflows. All 23 attempted actions matched the development oracles; that diagnostic count does not retroactively credit the three rejected workflows. Two attempts still misstated the carrier conflict/code assessment. A third chose a genuinely failed age condition as its reason, but the validator required an earlier failed status check. The [complete report](evidence/qwen-v4-relations-development.json) preserves all three failures.

The business policy requires every eligibility condition to pass and does not rank sufficient reasons for manual review. The supported-reason contract accepts any independently verified failed condition, rejects a reason naming a passing condition, and accepts `all_pass` only when all six checks pass. Every assessment, chosen action and citation still requires validation. Rendered text says "One reason for manual review" and handles unknown or future event age explicitly. No old execution is relabelled as passing.

## Architecture probes and final calibration

Two development-only final-turn replay probes used captured observations without replaying the previous answer. Renaming the carrier-check field did not repair either of two known chronology cases. A smaller action-only schema and instruction then produced 4/7 correct actions: two chronology cases and a shipment-status case selected incorrect investigations. These probes changed scaffolding and are not full workflow or unseen results. They justify rejecting those particular implementations, not a general causal claim about all checklists or field names.

The retained structured protocol keeps intermediate generation but narrows its authority as described above. Regression tests require false intermediate assertions and unsupported reasons to leave the evidence-derived explanation unchanged; a correct intermediate checklist cannot rescue a wrong action or invalid citation. Earlier 18/23, 22/23 and 20/23 workflow reports stay unchanged. The final protocol requires a complete new 23-case development calibration before the sealed challenge is opened.

The [final development run](evidence/qwen-v4-guarded-development.json) at clean source `9f9b245` records 23/23 correct actions, workflows and completions, with zero unapproved or duplicate effects. Both original below-threshold failures select manual review and display exact truthful age comparisons. Two intermediate carrier-check assertions and their reasons remain unsupported; the application renders the correct chronology explanation instead. These are exposed calibration cases, not fresh acceptance evidence. The runner retains the frozen 30-case numerical gates; their absolute thresholds are not acceptance criteria for a 23-case development run.
