# Casework Agent

An AI operations assistant that resolves a simulated delivery exception by looking up an order, checking policy and proposing a customer-service action across separate APIs. A human approves the final state change.

Status: proposed project. This repository contains a brief and evaluation design; there is no working agent yet.

## What it demonstrates

Business integration, tool schemas, multi-step execution, durable state, evaluation and human approval. The project addresses the full-stack delivery requirements in [OpenAI's London FDE role](https://openai.com/careers/forward-deployed-engineer-london-london-uk/). An MCP adapter can expose the same typed domain tools as the HTTP API.

## First release

An operator opens a synthetic exception, watches evidence arrive from an order service and carrier service, reviews the proposed resolution and approves or rejects it. On approval, the agent creates a local service ticket and records the action in a mock order system. All services and identities are synthetic and runnable locally.

The model selects permitted tools and drafts a resolution. Deterministic code owns policy checks, approval validation and writes. No real customer message, payment, refund or production mutation is in scope. Record why an action was proposed and the exact evidence shown to the reviewer.

## Proposed design

Web inbox -> Python API -> durable workflow state machine -> typed read tools -> proposal -> approval -> bounded write executor -> audit log. Model output must validate against a schema. Approval binds the exact proposal payload and its version. A changed proposal requires new approval. The executor uses idempotency keys and verifies remote state after an uncertain response.

Include local order, carrier and ticket services so integration boundaries are real even though the business data is fictional. Persist workflow and approval state in a transactional database. Distinguish a retryable timeout from an ambiguous write result; reconcile the latter before retrying. Present steps, evidence, pending approval and failures in the UI.

## Acceptance criteria

The application completes the scenario with actual local API calls. Read steps can retry within a fixed budget. Duplicate requests cannot create duplicate tickets. Process restart cannot bypass approval. Malicious instructions inside an order note cannot expand tool permissions. A user can cancel before the write or see its confirmed outcome afterwards.

## Scope limits

One exception workflow, one human approval and three local services. No multi-agent swarm, general-purpose browser automation or live business account integration. A deterministic workflow is the baseline; the agent must demonstrate where flexible reasoning helps rather than replacing every rule with a prompt.

## Policy contribution

The [specification](docs/SPEC.md) defines a conservative delivery policy and the exact permitted fictional writes. Matthew can optionally add 5-10 lines of policy preferences or internal-note wording; implementation can proceed with the documented defaults. See [evaluation design](EVALUATION.md).

## Licence

Original code and documentation: [MIT](LICENSE). Third-party datasets, models and media retain their own terms.

## Build handoff

Planning is documented; implementation has not started. Read the [specification](docs/SPEC.md), [10-task implementation plan](docs/superpowers/plans/2026-10-15-v1.md), [copyable chat handoff](CHAT-HANDOFF.md), [project instructions](AGENTS.md), [release standard](docs/RELEASE-STANDARD.md) and [honest current state](docs/STATE.md). The assigned fork builds this independent child under native superpowers:executing-plans.

The fixture baseline is free of model dependencies and is labelled as a deterministic workflow. Actual AI acceptance uses a separately measured, pinned Qwen/Qwen2.5-1.5B-Instruct snapshot through project-local MLX LM and held-out evidence. Ports are API8112, web5112, order8212, carrier8312 and ticket8412 on loopback. A model subprocess must acquire the shared resource lease before loading and exit before releasing it; no model server or cloud account is required.
