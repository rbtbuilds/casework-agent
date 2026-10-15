# Casework Agent working instructions

These instructions supplement `/Users/matthewgoralczyk/BentoLabs/portfolio/AGENTS.md`. This chat owns only `/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent`.

## Entry and authorization

- The first word of every reply is `Matthew`.
- Before any write, read the absolute CHAT-HANDOFF.md, parent/child AGENTS.md, README.md, docs/SPEC.md, EVALUATION.md, docs/RELEASE-STANDARD.md, plan and docs/STATE.md. A fork may inherit `/Users/matthewgoralczyk/Desktop/BentoLabs/resume`; explicitly set every shell workdir to this child and prove it with `pwd`.
- Planning is complete as documentation only. Begin implementation when Matthew pastes the execution prompt or otherwise explicitly requests it. Use native `superpowers:executing-plans`; do not rediscover settled product scope or initiate a per-task agent cascade.
- Inspect existing files, Git root/status/history, processes and ports before acting. No Git repository existed at planning time; reality may have changed. Initialize only this child if it remains absent and use branch `feat/casework-agent-v1`. Never initialize or publish the portfolio parent.
- Read every changed file plus relevant callers/consumers/tests before editing. Preserve unrelated edits. Scope changes, missing human-only decisions and hard-to-reverse actions require confirmation; reversible authorized implementation does not.
- Local scoped commits are part of an execution handoff. Public repositories, push, release, deployment, paid compute, uploads, real emails and external sends need specific authorization. Never use the resume app panel to commit this child accidentally.

## Runtime and isolation

- Use Python 3.12.x through uv and `requires-python = ">=3.12,<3.13"`; local `.venv`, lockfile and dependencies only. Use Node 24 LTS via an available local manager; document a tested local exception if unavailable, with CI remaining Node24. No global runtime or configuration changes.
- Reserved loopback ports: API8112, web5112, order8212, carrier8312, ticket8412. Vite uses strictPort. A busy port requires owner inspection, never silent reassignment or an unowned process kill.
- Keep `.runtime`, data, service databases, reports, secrets and model assets local/ignored. Persist only explicitly curated synthetic evidence. Every service owns its database; the application accesses mocks through HTTP only.
- Record process PID, start token, arguments and owner nonce. Stop only verified owned children; no `killall` or broad process matching.
- Before any weight load, real-model run or heavy evaluation, atomically acquire `/tmp/bentolabs-portfolio-ml.lock` with mkdir; write project/PID/UTC start/purpose/nonce. Unload the model or confirm owned server exit before releasing only this matching lease in finally/trap. If cleanup fails, keep the lease and report the still-live process.
- A busy lease means continue light work; no spinning, deletion, simultaneous model server or silent fixture substitution. Inspect stale ownership and the actual process before recovery; PID equality alone is insufficient.

## Correctness and evidence

- The model proposes through bounded read tools; deterministic code owns policy, approval and writes. All data and side effects are fictional. No refund, payment, customer contact or privileged model tool. The executable default is the public Apache-2.0 Qwen/Qwen2.5-1.5B-Instruct checkpoint through project-local MLX LM; explicitly pin/download/hash its snapshot during implementation.
- Bind approval to exact immutable proposal ID/hash/version, policy and evidence versions. Stale/expired proposals need new approval. Transactionally arbitrate cancellation versus first execution claim.
- Persist immutable operation key/body/hash before network writes. An ambiguous response is unknown until reconciled with the remote journal. Reuse only the same key/body; never mint a key to bypass uncertainty.
- Remote services atomically commit each idempotency journal with the domain mutation. This gives bounded local per-key protection, not distributed exactly-once execution or cross-service rollback. Expose unknown and partial outcomes accurately.
- Fixture mode, model protocol tests and actual model inference are distinct labels. No existing weights/server is assumed. Implement the default model in an owned subprocess with typed pipe messages and prompt-generated schema-validated tool JSON. No endpoint, paid resource, API key or model decision is required from Matthew. Acquire the resource lease before loading, and confirm child exit/unload before release. Only an actual download/runtime/probe/evaluation failure blocks the real gate.
- Follow the SPEC UI system from the first pass: typography, spacing, both palettes, responsive layout, accessibility and reduced-motion behavior. Read an applicable design skill before UI implementation; finish with a plain visual detail review.
- Source/code punctuation is ASCII. Tests are typed: Ruff, strict Pyright including tests, strict TypeScript including Vitest/Playwright, pytest, Vitest, build and actual-service browser flows are required.
- Use docs/STATE.md for exact progress, commands, versions, evidence, failures, skipped checks and next action. Do not pre-check gates or fabricate results. Review all changes before integration; no claim of implementation from file presence alone.

## Shared-work boundaries

Do not edit siblings, parent coordination files, resume, project registries, machine configuration or vault. Do not launch sibling chats, automations or monitors. Report a necessary parent change in this chat. Operations-record integration belongs to the coordinating parent; report verified outcomes for that update without inventing an unavailable database result.
