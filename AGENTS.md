# Casework Agent agent guidance

## Scope and entry

- Work only inside this repository's verified checkout. Confirm the working directory, Git root, branch, status and remotes before writing. Never initialize or publish a parent folder.
- Read any applicable parent AGENTS.md before editing. Changes must remain within this repository; do not modify sibling projects, external workspaces or machine configuration.
- Read README.md, docs/STATE.md, docs/SPEC.md, EVALUATION.md and docs/ENGINEERING-DECISIONS.md. The application already exists. CHAT-HANDOFF.md and the original ten-task plan are historical implementation records, not instructions to reinitialize or rebuild it.
- Read changed files, callers and relevant tests before editing. Preserve unrelated work. Use feature branches for changes and scoped commits when requested. Do not force-push or rewrite published history.

## Runtime and ownership

- Use Python 3.12 through uv, a project-local `.venv`, and locked dependencies. Use Node 24 LTS; a different supported local version requires explicit recorded verification. Do not replace global runtimes.
- Reserved loopback ports: API 8112, web 5112, orders 8212, carrier 8312 and tickets 8412. Vite uses strictPort. Never change ports to hide a collision or stop an unrelated listener.
- Keep runtime state, databases, dependencies, secrets and weights ignored. Each mock owns a separate SQLite database; application business calls cross HTTP.
- Use `scripts/dev.py start|run|status|stop` for the developer stack. Stop only processes whose PID, start time, arguments and owner nonce match the record. If a demo was already running, preserve its databases and restore it after process tests.
- Acquire `/tmp/bentolabs-portfolio-ml.lock` atomically before loading weights or actual-model evaluation. Record project, PID, process start identity, UTC start, purpose and owner token. A busy lock means report model_busy and continue lightweight work; never steal it or spin.
- Confirm the owned model child has exited before releasing only the matching lease. If cleanup fails, retain the lease and report the live process. No unleased resident model worker.

## Correctness and verification

- The model can read only the case's order, shipment and policy. Deterministic code validates policy and citations, compiles intents, binds exact approval and authorizes writes. All business data and effects remain fictional.
- Approval binds the immutable proposal hash, source versions, policy and expiry. Superseded evidence cannot authorize a newer cached snapshot. Gathering success, failure and trace writes must match the saved run and current worker generation.
- Persist operation key, body and hash before HTTP. Treat ambiguous writes as unknown and reconcile the same journal key. Never mint a replacement key or silently change a saved payload. Expose partial completion accurately.
- Add a failing regression for substantive correctness fixes. Run Ruff, strict Pyright including tests, pytest, strict TypeScript including browser tests, Vitest, build and actual-service Playwright as appropriate. Run port-owning suites sequentially. Regenerate API contracts when their source changes.
- Before UI implementation, follow the existing design system in SPEC.md and read an available relevant design skill. Preserve light/dark themes, responsive layouts, keyboard controls, visible focus and reduced motion. Finish with visual inspection.
- Use ASCII punctuation in source. Comments explain constraints rather than narrating code. Prefer a small direct change to an unnecessary abstraction.

## Evidence, documentation and publication

- Distinguish fixture runs, scripted model-protocol tests and actual inference. The pinned Qwen/MLX v1 run failed its quality gate; do not present fixture results as model quality or tune against the frozen holdout.
- Preserve frozen inputs and measured reports. A new run or correction needs explicit provenance and updated hashes, not a silent rewrite. Keep model licences separate from the MIT code licence.
- Update docs/STATE.md with actual checks, failures, skipped checks and relevant source commits. Record limitations candidly. Do not claim production validation, distributed exactly-once execution or an unperformed human review.
- Keep README and RUNBOOK commands portable. Do not embed a contributor's machine path into runtime configuration. Historical benchmark paths are provenance, not required installation locations.
- Repository publication and pushes require a direct user request. Deployment, releases, paid resources, model uploads and messages to others each require their own authorization. Never upload weights or private data with the source repository.
