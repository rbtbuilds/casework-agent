# Case study: a local agent with explicit authority and recoverable effects

A delivery-exception operator must combine an order, carrier history and policy before opening an internal investigation. The action crosses two systems: create a ticket, then annotate the order. If evidence changes or a write response disappears, the application must preserve what was approved and distinguish a failed request from an unknown outcome.

Casework Agent demonstrates that workflow with local Qwen3 14B inference, FastAPI, React/TypeScript and four independent SQLite databases. All records and effects are fictional. [Watch the browser demonstrations](WALKTHROUGH.md).

## The engineering work

**Constrain the model's scope.** Qwen chooses three case-scoped read tools, evaluates six policy conditions in separate contexts, then selects an action and reason from its unchanged answers. Schema constraints leave both Boolean values and both actions available. The application independently validates claims, citations, policy and source versions. Semantic mistakes fail without correction, a second choice or fixture substitution. Exact arithmetic and UTC relations are supplied features.

**Bind authority to an immutable proposal.** Application code renders the displayed explanation and exact note from observed evidence. Approval binds their proposal hash, source versions, policy and expiry. The browser sends that exact identifier/hash and its current case version; stale evidence cannot authorize a newer proposal. The model has no write tools.

**Persist before sending.** A fenced worker saves each operation's key, payload and hash before HTTP. The dependent annotation uses the confirmed ticket ID and approved order version. A missing response remains unknown until a matching remote journal confirms it, or a bounded identical-key replay resolves it. Partial results remain visible. This provides per-key duplicate protection in the simulation; there is no cross-service rollback or distributed exactly-once guarantee.

## What the evidence supports

The first frozen v5 challenge produced **30/30 correct actions/outcomes, 180/180 correct model conditions and 24/24 authorized completions**, with six deliberate stale approvals producing no writes. The same-input fixture comparison is separate. All 300 actual-model requests remain available; no semantic retries or replacement answers occurred. Warm workflow p50 was 18.03 seconds and p95 24.77 seconds on the recorded Apple Silicon configuration.

The [retained-evidence audit](EVIDENCE-AUDIT-2026-10-17.md) recomputes conditions independently and binds proposals, approvals and operation payloads to the original remote journals and effects. Its semantic review of displayed prose is explicitly AI-assisted. Human factual-review fields remain pending.

The browser demonstrations show source gathering, zero writes before exact approval and one confirmed pair afterward. A separate fixture clip drops both write responses after commit and shows the retained uncertainty/recovery events. Complete process tests additionally cover restart boundaries, generation fencing, stale approvals, interrupted gathering and partial conflicts. [Verification state](STATE.md) records exact commands, counts and limitations.

## What changed after failure

The original 1.5B run achieved 0/30 valid actions. Later protocols still made age, missing-timezone and intermediate-claim errors. Those reports remain frozen. Isolating each condition fixed the retained v5 cases without feeding validator answers back to the model. A separate shutdown defect required a workflow fix to persist partial traces and propagate cancellation. Model quality and durable execution needed distinct tests.

This is a guarded workflow and recovery demonstration. The deterministic validator already knows the fixed policy, so the model does not establish a decision-quality advantage over ordinary code. The small AI-authored synthetic challenge does not estimate production accuracy or customer savings. Published cases are now exposed; later executions are reproductions. Public authentication, tenant isolation and manual screen-reader verification remain outside the completed work.

See [evaluation and frozen history](../EVALUATION.md), [runbook](RUNBOOK.md) and [publication audit](PUBLICATION-AUDIT.md) for source identities, reproduction and evidence boundaries.
