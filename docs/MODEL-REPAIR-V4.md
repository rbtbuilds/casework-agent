# Grounded policy decisions and explanations

V3 met the numerical action targets but retained two wrong age comparisons, three wrong assessment fields alongside correct decisions, two incorrect rationales, premature escalation wording and an imprecise timestamp note. The original inputs, model replies and reports remain frozen. This repair changes the internal model protocol; the operator API, business policy, exact approval and durable HTTP execution stay in place.

## Responsibility and validation

Qwen reads the scoped order, shipment and policy, generates all six assessment booleans, chooses a primary reason and selects the action. Both boolean values, every reason and both actions remain available in the generation schema. The model receives exact policy-relative arithmetic: event age minus the policy threshold in integer microseconds. A negative distance is below threshold; zero is exactly at it. This simplifies a policy comparison and is not evidence of unaided model arithmetic. Rounded floating-point hours are absent from the decision context.

After generation, the application independently checks every assessment against raw observations and requires the first failed condition, or `all_pass` when every condition passes. It also validates the chosen action, evidence scope, hashes and citations. A semantic mismatch fails gathering without publishing a proposal, replacing an answer or returning correctness feedback. Raw replies remain in the trace. The one protocol-repair budget does not apply to semantic failures.

The model response contains no free-form rationale or note. After validation, `validated-reason-renderer-v1` renders those fields from the selected reason and controlled observed values. It distinguishes an absent timestamp from a present timestamp without timezone, identifies inconsistent chronology, retains exact age values and uses prospective action wording. It does not copy untrusted notes, event descriptions or arbitrary exception text. The model therefore performs structured retrieval and decision selection; the application writes the displayed explanation. This is a deliberate limit on generative prose, not a free-text factual-accuracy claim.

All temporal comparisons normalise aware datetimes to UTC before subtraction or ordering. Unknown timezones remain unknown. UTC conversion failures stop model gathering safely; the deterministic policy conservatively selects manual review for unrepresentable clocks. Regressions cover spring daylight-saving differences and ambiguous autumn scans using shared timezone objects.

## Verification and evaluation procedure

1. Reproduce the publication gap with correct actions carrying false assessments, then add strict semantic validation.
2. Exercise threshold distances below, equal to and above zero, every exclusion, absent/naive clocks, UTC bounds, early proposals, scope errors, hostile text and bounded prospective explanations.
3. Run strict Python and TypeScript checks, complete software tests, contract reproduction and actual-service browser recovery. Model inference uses the shared machine lease; fixture checks remain separate.
4. Calibrate on `fixtures/manifests/v4-development.json`. Its 23 exposed regression cases include 16 earlier development inputs and seven previously published v3 cases. These are not unseen evaluation.
5. Freeze implementation, prompt, schema and model identities before opening the separately authored v4 challenge. Promote the author's exact input bytes, record the first run and compare the same-input fixture workflow. Any later rerun is reproduction or diagnostics.
6. Review all model choices and rendered explanations against observations. Model-assisted review does not satisfy the required human review. Keep known failures and pending review visible in the public acceptance record.

The selected model remains the pinned Qwen3 14B checkpoint recorded in [MODEL-CONFIG](MODEL-CONFIG.md). New measurements and their source commits belong in [STATE](STATE.md) and [EVALUATION](../EVALUATION.md). Historical scores are not a controlled model-only comparison.

## Development finding: condition grouping

The first v4 calibration at `1631ede` accepted 18/23 cases. Every age-boundary case passed, but five assessment mismatches were blocked. Four involved chronology; three of those also incorrectly labelled a timestamp fault as a carrier conflict. Another overstated the shipment-status check. The [failed report](evidence/qwen-v4-initial-development.json) remains unchanged.

The next experiment replaces the flat computed-facts block with six `CHECK_INPUTS` groups keyed by the assessment fields. Conflict input contains only the recorded flag and normalized codes; chronology contains every UTC timestamp and signed offset in source order, without statuses, codes or the age threshold. Grouping is organizational guidance inside one prompt, not a separate security boundary. It supplies no predicate outcomes and changes neither the response choices nor semantic validation. The entire same exposed development set is used for comparison.
