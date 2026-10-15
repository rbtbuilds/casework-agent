# Casework Agent chat handoff

This handoff is self-contained. Paste the prompt below into the fork that will own Casework Agent. Forks may inherit the resume directory; the explicit paths are part of the safety boundary.

## Copyable execution prompt

```text
Implement Casework Agent v1 using the approved specification and plan. I authorize reversible local implementation, dependency setup within this child, tests, fixture runs, explicit download of the public Qwen/Qwen2.5-1.5B-Instruct snapshot, local inference/evaluation under the shared resource lease, and scoped local commits. Work only in /Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent and use branch feat/casework-agent-v1. This is one of five independent projects being built in separate chats.

Before any write, read these absolute files:
/Users/matthewgoralczyk/BentoLabs/portfolio/AGENTS.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/AGENTS.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/CHAT-HANDOFF.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/README.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/docs/SPEC.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/EVALUATION.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/docs/RELEASE-STANDARD.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/docs/superpowers/plans/2026-10-15-v1.md
/Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent/docs/STATE.md

Set every shell tool's workdir explicitly to /Users/matthewgoralczyk/BentoLabs/portfolio/casework-agent and verify pwd. Inspect actual files, Git root/status/history, local runtimes and listeners before resuming. A fork may still show the resume repository in the app; do not use an unrelated Git panel. No child Git root existed when planning finished. If it is still absent, run git init -b feat/casework-agent-v1 only in this child and preserve/commit the planning scaffold on that owned branch. If state differs, inspect and preserve it; do not overwrite or initialize a parent repository. Never change global Git configuration.

Read and use the installed superpowers:executing-plans skill at /Users/matthewgoralczyk/.codex/plugins/cache/claude-plugins-official/superpowers/6.4.1/skills/executing-plans/SKILL.md. Execute natively, task by task, with tests and local commits. The scope and architecture are settled; do not restart discovery or ask me to choose an execution style. Do not launch a per-task subagent cascade or create more chats. Apply required verification and review without exceeding this authorization.

Build Python FastAPI/SQLite plus React/TypeScript/Vite, with real independent fictional order/carrier/ticket HTTP APIs, durable approval/execution/recovery, a clearly labelled fixture baseline and an actual bounded Qwen tool-use adapter. Default to Qwen/Qwen2.5-1.5B-Instruct with project-local MLX LM and a pinned, hashed public snapshot. Run inference in an owned subprocess, accepting only schema-validated JSON read-tool requests or a proposal; no native function-calling server is required. Use the fixed conservative policy in SPEC.md; my optional 5-10 lines of policy wording are useful but not a prerequisite. All writes are synthetic tickets and order annotations, never real emails, refunds or payments.

Use Python3.12.x via uv and local Node24 LTS via an available manager, or record a verified local exception with CI on Node24. Keep separate .venv, web/node_modules, .env, .runtime and databases. Bind API8112/web5112/order8212/carrier8312/ticket8412 to 127.0.0.1, use strictPort and exact CORS, and fail clearly if occupied. Inspect ownership before stopping only your own processes; do not change ports or kill unrelated processes.

Acquire /tmp/bentolabs-portfolio-ml.lock atomically before any model load or real-model evaluation; record owner/project/PID/UTC start/purpose/nonce. Load the pinned default snapshot only in your owned local worker under that lease. Unload or confirm process exit before releasing only your matching lease in finally/trap. If busy, continue light tasks and report model_busy; never delete the lease, spin, keep an unleased resident process or silently substitute fixtures. No existing model/server is assumed and no server/model configuration is needed from me. Explicitly download the public checkpoint locally, probe compatibility and run the real-model gate. Only an actual access/runtime/probe/evaluation failure can block that gate; record it precisely and finish independent work. No cloud keys or paid resources.

Run strict Pyright and TypeScript checks including tests, Ruff, pytest, Vitest, build and Playwright against the actual services. Exercise approval replay, stale proposals, cancellation races, crashes, uncertain writes and partial outcomes end to end. Report fixture and real-model evidence separately; never claim distributed exactly-once or fabricate benchmark results.

Keep docs/STATE.md current with task status, exact commands/commits, versions, measured reports and hashes, failures/skipped checks, owned processes and next action. Do not edit siblings, the portfolio parent, resume, vault, machine configuration or project registries. Public GitHub repositories, push, release, deployment, model uploads, paid compute and external sends require my specific approval. Stop only the dependent task when an external input is missing and complete the remaining authorized work. Start every reply with Matthew.
```

## Expected outcome

A local, fixture-verified workbench plus a separately measured run of the pinned Qwen model through MLX LM. If a concrete download/runtime failure prevents that run, report fixture completion and the exact blocked model gate; if measured quality misses a threshold, report the failed threshold. Never present an unlabeled deterministic demo as AI.

The next chat should report its actual implementation state, safety/failure-matrix results, model evidence status and precise run commands. No push or publication is authorized by this handoff.
