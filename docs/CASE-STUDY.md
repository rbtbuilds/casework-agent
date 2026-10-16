# Case study: an approved action with recoverable effects

A delivery-exception operator needs an order record, carrier history and the applicable policy before opening an investigation. The next steps cross two systems: create an internal ticket, then annotate the order. A model can select an action from evidence, but the workflow must preserve the operator's authority when evidence changes or a service response disappears.

Casework Agent implements that workflow with local Qwen inference, a React workbench, FastAPI and four independent SQLite databases. All business records are synthetic; no customer pilot or time saving is claimed.

## Keeping authority explicit

Qwen has three scoped read tools. Schema-constrained generation binds tool identifiers and citations to the current case, while leaving both final actions available. The model chooses the action. Deterministic validation checks that choice against policy without returning an answer for a second attempt. The application writes its own policy explanation and internal note from the observed evidence. Intermediate model assessments and reasons remain diagnostic, with errors preserved; they cannot change the displayed explanation.

Approval binds the proposal hash, cited evidence, source versions, policy and expiry. A fenced worker saves each operation's key, body and hash before sending it over HTTP. The order annotation uses the confirmed ticket identifier and the approved order version.

The browser recovery test drops each service's first response after its transaction commits. The outcome becomes unknown; a matching remote journal then confirms it. One ticket and one annotation remain. A separate conflict test preserves a confirmed ticket when the annotation is rejected and shows a partial result. These tests establish bounded behavior in the simulation, without a distributed exactly-once guarantee or cross-service rollback.

## Learning from failed inference

The original Qwen2.5 1.5B adapter produced 0/30 valid actions because free-form generation broke the JSON/evidence protocol. Constrained decoding fixed the protocol boundary. Qwen3 4B reached 29/30 on development cases, then only 17/30 on a newly authored challenge, with 14/24 authorised completions. Its wrong proposals stopped before writes. Both failed evaluations remain published with their original source and model identities.

That gap showed why calibration could not establish model quality. The first Qwen3 14B development check passed only 12/16: a larger checkpoint and corrected rendering still missed shipment-status and carrier-event exclusions. The current protocol requires the model to assess each of the six policy conditions before choosing its action. It also disables the checkpoint's thinking mode explicitly and renders the latest evidence, factual summary and schema together. Escaping content at the final rendering boundary prevents business data, replayed model replies and repair errors from introducing chat-role delimiters. The model receives copied fields, UTC timestamps and exact signed time differences, with no action oracle. Its assessment booleans remain model-generated claims; the backend independently validates the final action.

The v3 challenge was authored separately without access to the current model implementation or development outputs. Its inputs stayed private until implementation freeze. The model and fixture use the same 30 cases and fault schedule; six cases require stale rejection, and 24 expect a completed ticket/annotation pair. Each benchmark records source, prompt, model and input hashes.

## Measured v3 outcome

At clean source `a79256d09cf2dc8b1e8964ec910b826a8dd1e7c1`, the first v3 run produced 28/30 correct actions, 28/30 expected final outcomes and 22/24 authorised completions. The same-input fixture achieved 30/30 and 24/24. Both runs observed zero unapproved writes and duplicate effects. The model's assessment and generated prose still need human factual review.

The source was frozen at `3c5a2377bf759e9b8aee231a6c1fb547a115cdb4` before the implementer opened the challenge. The subsequent data-only commit preserved its input bytes. These results measure the complete guarded model workflow, including constrained reads/citations and independent policy validation. They do not isolate a model-size effect; the historical runs used different case sets and protocols.

Two below-threshold generations falsely claimed that the event age met 48 hours. Exact policy validation rejected both before proposal publication, approval or writes. Their traces retain the one-second and one-microsecond shortfalls. A model-assisted trace review also found three incorrect assessment fields among correct decisions, two incorrect rationales, two premature escalation notes and one imprecise timestamp note. These findings are detailed in [the source and trace review](REVIEW-2026-10-16.md). Human factual review remains pending; action accuracy does not certify explanation accuracy.

## V4: separating action selection from explanation

The remaining age errors motivated exact signed policy-relative arithmetic and explicit UTC temporal relations. Strictly validating redundant model assessments exposed additional failures, while an action-only experiment also reduced accuracy. Those failed development results remain published.

The retained model selects the action after structured intermediate generation. Its booleans and selected reason have no authority over explanations or execution. Code independently validates the action and citations, then derives a prospective policy explanation from raw observations. The original broader factual-review gate remains unchanged.

After 23/23 exposed calibration cases and actual-model browser recovery passed, source and model identities were frozen before opening a separately authored 30-case challenge. The first run records **29/30 correct actions**, **29/30 correct final outcomes** and **23/24 authorised completions**; the same-input fixture records 30/30 actions/outcomes and 24/24 completions. Both observed zero unapproved and duplicate effects. The fresh run retains 2 incorrect intermediate assessment fields across 2 attempts and 2 unsupported selected reasons. These are recorded in trace diagnostics and cannot change displayed explanations or authorise writes. Human review remains pending; the broader zero-unsupported-claims gate is not claimed.

The model's action remains independently selected and may fail validation. For this fixed policy, code already knows the permitted answer, so these measurements establish a guarded inference/workflow demonstration rather than a model advantage over deterministic logic. The application-generated explanation is not a claim about Qwen's reasoning.

## Operating limits

The workbench is a loopback, single-operator simulation with synthetic data. Human review of generated factual claims, manual screen-reader testing and a recorded walkthrough remain pending. Automated checks cover keyboard approval, both themes, desktop/mobile layouts and reduced motion. Model failure never switches silently to fixture mode. Weights, databases and runtime output stay outside Git.

See [evaluation](../EVALUATION.md), [model configuration](MODEL-CONFIG.md), [verification state](STATE.md) and [publication audit](PUBLICATION-AUDIT.md) for reproducible evidence and its limits.
