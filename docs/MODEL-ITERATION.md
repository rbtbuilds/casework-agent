# Repairing local model inference

The original Qwen2.5 1.5B evaluation produced no valid proposals in 30 cases. Its process loaded successfully, but free-form generation omitted required arguments, skipped evidence reads and invented citation IDs. Those failures stopped before approval or writes.

## Structured generation

The current adapter passes a JSON Schema to an Outlines logits processor inside the MLX worker. The tokenizer's checkpoint-provided chat template is applied once. The decoder permits only unread tools and identifiers belonging to the current case. A proposal becomes available after order, carrier and policy evidence have been fetched; its citation array contains those actual observations.

Both final actions remain available to the model. The decoder receives no oracle action, eligibility result, expected workflow state or fault label. Deterministic validation rejects an incorrect action immediately. Policy errors receive no second attempt, so the evaluator cannot credit a correction prompted by a binary policy-answer signal. One repair remains available for malformed protocol requests from a compatible client.

Before the proposal, a compact context message repeats the fetched status, exception, conflict and event fields. Its elapsed-hours value is ordinary timestamp subtraction using the case's business clock. Missing or timezone-naive timestamps produce an unknown age. This summary contains no action recommendation; the original observations and their hashes remain in the trace.

The model now generates an assessment of each policy condition before its rationale and action. Each boolean is an unrestricted model output. The prompt requires short explanations grounded in the supplied fields, identifying the first failed condition or why all six pass. Exact approval still covers the generated note, including any factual error an operator needs to reject. Action validation does not certify free-text factual accuracy.

## Development comparisons

Five cases, one from each existing development family, were used for the initial comparisons. They are calibration examples, with no claim of unseen evaluation.

| Candidate and protocol | Valid actions |
| --- | --- |
| Qwen2.5 1.5B, structured JSON | 2/5 |
| Qwen2.5 7B 4-bit, same prompt | 3/5 |
| Qwen2.5 7B 4-bit, rationale-first prompt | 3/5 |
| Qwen3 4B Instruct 2507 4-bit, rationale-first prompt | 5/5 |

The first three prototypes permitted policy feedback during repair and are excluded from acceptance evidence. The Qwen3 comparison rejects wrong policy decisions without feedback. Its five correct actions still included misstated dates and a shipment status in free text. That observation motivated the compact field summary and exact elapsed-hours calculation before the larger development run.

Candidate selection changed both model and context engineering. These comparisons cannot attribute improvement to either change alone. The original 0/30 benchmark remains preserved at its measured source and model revision.

The larger development run then produced 29/30 correct actions and completed workflows, with zero unapproved or duplicate effects. Its single missing-timestamp case recognised unknown age in prose but selected investigation; validation rejected it without approval or writes. The full report is [preserved here](evidence/qwen-v2-development-full.json). Its source tree was in progress and is recorded as dirty; it is calibration evidence.

The final prompt makes the existing chronology policy explicit: missing or timezone-naive clocks, future summaries, and event scans newer than the last-event summary require manual review. The [six-case development regression check](evidence/qwen-v2-final-development-check.json) then completed 6/6, including the observed missing-timestamp failure. Final acceptance uses the separately frozen challenge, with its own source and prompt hashes.

## Runtime and reproducibility

The independently authored v2 challenge was promoted only after source freeze
`26643635f312e076dff75ea7905c742ddea7b195`. Its first actual-model run at clean
source `bd94e418e9b7f9df60709a9eb8801ef6555e0f2a` produced **17/30** valid actions
and correct workflows, with **14/24** authorised completions. All 13 incorrect
actions failed policy validation before approval or writes. There were zero
unapproved writes and duplicate effects. The [full model report](evidence/qwen-v2-challenge.json)
and [same-input fixture report](evidence/fixture-v2-challenge.json) preserve this
failure; the fixture completed 30/30 workflows and 24/24 authorised actions.
Generated claims still lack human review. The 4B candidate failed the quality
gate despite its stronger development results.

At the next development checkpoint, the implementation tested a pinned 14B Qwen checkpoint, explicit
non-thinking rendering, and one final user turn containing the latest evidence,
compact facts and response schema. The v2 renderer put the schema in a separate
last user message. JSON serialization now escapes angle brackets so business
text cannot insert raw tokenizer role delimiters. These changes do not change
the policy or supply an action. At that checkpoint, the new independently authored v3 challenge stayed
private until source freeze. V2 inputs and results remain immutable.

The first 14B development run passed **12/16** cases with zero unapproved or
duplicate effects. The model quoted an excluded shipment status correctly but
still chose investigation; it also missed three carrier-event exclusions.
Its [report](evidence/qwen-v3-initial-development.json) remains calibration
evidence. A larger checkpoint and corrected rendering alone did not establish
adequate policy reasoning. The next development change requires an explicit,
model-generated assessment of each policy condition before the action, with
neutral timestamp differences to reduce calendar arithmetic. Those assessments
are model outputs, not supplied eligibility answers. The independent challenge
was still unopened at that checkpoint.

The assessment protocol also supplies exact signed integer microsecond differences
for event age and chronology, plus UTC timestamp copies and lowercased event
codes. These are arithmetic and normalization of observations, with no policy
predicates or action recommendation. Null differences preserve unknown or naive
timestamps. The prompt describes the unchanged six conditions in order and
requires proposed-action wording in the internal note. The decoder does not
force a condition to pass or fail, and the backend does not derive its action
from the model's checklist. Incorrect policy choices still fail once, without
answer feedback. This iteration was checked on the same development inputs;
the private challenge had not been opened.

Model preparation uses named profiles with immutable public revisions. A checkpoint's separate `.jinja` chat-template file is downloaded and hashed alongside its configuration, tokenizer and weights. A temporary pointer replaces the selected snapshot only after the download and hashing complete. The original 1.5B profile remains available.

An owned subprocess loads the verified snapshot under the shared machine lease. Model execution is offline; Outlines caches stay in the project's ignored runtime directory. Probe and benchmark identities come from the snapshot captured by that session, even if another preparation changes the selection pointer. Readiness requires the matching snapshot hash and protocol version.

The full report records the model revision, snapshot hashes, system-instruction hash, per-turn generation-schema hashes, actual exchanges, usage, timings and source revision. Public exports preserve measurements while removing workstation paths and process-ownership metadata, and identify their original report by SHA-256.

See the [model configuration](MODEL-CONFIG.md), [evaluation contract](../EVALUATION.md) and [runbook](RUNBOOK.md) for the selected checkpoint and commands. The JSON Schema integration follows the [Outlines MLX documentation](https://dottxt-ai.github.io/outlines/latest/features/models/mlxlm/).

## Development evidence

- [1.5B structured prototype](evidence/qwen-v2-1.5b-development-smoke.json): 2/5.
- [7B with the same prompt](evidence/qwen-v2-7b-development-smoke.json): 3/5.
- [7B with rationale first](evidence/qwen-v2-7b-reason-first-smoke.json): 3/5.
- [Qwen3 4B comparison](evidence/qwen-v2-4b-development-smoke.json): 5/5, before compact fact preparation.
- [Full development run](evidence/qwen-v2-development-full.json): 29/30, before the final chronology clarification.
- [Final development regression](evidence/qwen-v2-final-development-check.json): 6/6.
- [Qwen3 protocol probe](evidence/qwen-v2-probe.json): schema-valid tool request, bound to its snapshot hash.

Every calibration report records its own prompt hash and in-progress source state. Counts from these development checks are not held-out acceptance results.

The explicit-assessment development run then passed **16/16** actions and
workflows, with 16/16 authorised completions and zero unapproved or duplicate
effects. Its [report](evidence/qwen-v3-development.json) preserves the same
16 development inputs as the initial 12/16 run. These are calibration results.
A subsequent UTC-boundary guard makes unrepresentable dates handled errors;
unit, HTTP-admission and same-worker continuation regressions cover that guard.
The final 30-case challenge was still unopened at source checkpoint
`3c5a2377bf759e9b8aee231a6c1fb547a115cdb4`.

## First v3 challenge result

After source freeze `3c5a2377bf759e9b8aee231a6c1fb547a115cdb4`, the separately authored v3 inputs were promoted
unchanged and measured at clean source `a79256d09cf2dc8b1e8964ec910b826a8dd1e7c1`. The first model run produced
28/30 correct actions, 28/30 expected final outcomes
and 22/24 authorised completions, with zero unapproved writes
and duplicate effects. [Full model report](evidence/qwen-v3-challenge.json) and
[same-input fixture comparison](evidence/fixture-v3-challenge.json) retain every
case. Numerical targets pass; factual-claim review remains pending. These results
measure the guarded workflow and do not isolate a model-size effect. All earlier
failures and calibration reports remain unchanged.
