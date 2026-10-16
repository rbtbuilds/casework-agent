# Maintenance handoff

Casework Agent v1 is implemented. Use this document to resume maintenance without repeating project initialization.

## Read first

- [README](README.md): supported setup, demonstration and project overview.
- [Current status](docs/STATE.md): verified source, CI evidence and outstanding limitations.
- [Specification](docs/SPEC.md): workflow, approval and recovery contracts.
- [Engineering decisions](docs/ENGINEERING-DECISIONS.md): architecture and tradeoffs.
- [Evaluation](EVALUATION.md): frozen split, metrics and measured results.
- [Runbook](docs/RUNBOOK.md): process ownership, model lease and recovery commands.
- [AGENTS.md](AGENTS.md): repository conventions for coding agents.

Confirm the working directory, Git root, branch, status and remotes before editing. Preserve existing work and use an isolated feature branch for new changes. The [original implementation plan](docs/superpowers/plans/2026-10-15-v1.md) records completed design work; it is not a bootstrap script.

## Maintenance constraints

Approval must remain bound to the exact proposal, cited evidence, source versions, policy and expiry. Persist every mutation's key and payload before sending it. Treat ambiguous writes as unknown until the matching remote journal confirms the outcome.

Process tests share the documented loopback ports and run sequentially. Use the ownership-checked lifecycle helper to stop services. Actual inference acquires the shared machine lease before loading weights and releases it only after the owned model child exits.

Keep fixture tests separate from actual-model evidence. The original 1.5B and v2 4B benchmarks failed their quality thresholds. The first frozen v5 actual Qwen result is 30/30 actions/outcomes, 180/180 generated condition fields, 30/30 supported reasons and 24/24 completions. Code supplies exact UTC features, Qwen evaluates each condition in an isolated context, and a final request selects action/reason from those unchanged outputs. All claims and the choice are independently validated without correction or semantic retry. Human factual review remains pending. All published challenges are exposed inputs, so future model changes require separate development and a newly sealed fresh set. Read docs/MODEL-REPAIR-V5.md, STATE.md and EVALUATION.md. A separately recorded post-measurement workflow correction preserves graceful-cancellation traces without changing inference. Preserve all frozen artifacts. Public authentication and production deployment are outside the implemented scope.

Record source changes, verification results and unresolved issues in docs/STATE.md. Keep contributor instructions portable and describe benchmark machines explicitly only where they establish measurement provenance.
