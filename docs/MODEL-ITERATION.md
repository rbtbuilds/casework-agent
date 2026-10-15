# Repairing local model inference

The original Qwen2.5 1.5B evaluation produced no valid proposals in 30 cases. Its process loaded successfully, but free-form generation omitted required arguments, skipped evidence reads and invented citation IDs. Those failures stopped before approval or writes.

## Structured generation

The current adapter passes a JSON Schema to an Outlines logits processor inside the MLX worker. The tokenizer's checkpoint-provided chat template is applied once. The decoder permits only unread tools and identifiers belonging to the current case. A proposal becomes available after order, carrier and policy evidence have been fetched; its citation array contains those actual observations.

Both final actions remain available to the model. The decoder receives no oracle action, eligibility result, expected workflow state or fault label. Deterministic validation rejects an incorrect action immediately. Policy errors receive no second attempt, so the evaluator cannot credit a correction prompted by a binary policy-answer signal. One repair remains available for malformed protocol requests from a compatible client.

Before the proposal, a compact context message repeats the fetched status, exception, conflict and event fields. Its elapsed-hours value is ordinary timestamp subtraction using the case's business clock. Missing or timezone-naive timestamps produce an unknown age. This summary contains no action recommendation; the original observations and their hashes remain in the trace.

The model writes its rationale before its action. The prompt requires short explanations grounded in the supplied fields. Exact approval still covers the generated note, including any factual error an operator needs to reject. Action validation does not certify free-text factual accuracy.

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
