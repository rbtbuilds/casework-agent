# Contributing

Use Python 3.12 and Node 24. Bootstrap with `uv sync --locked` and `npm --prefix web ci`. Run the commands in [RUNBOOK](docs/RUNBOOK.md) before proposing a change. Python checks cover application code, mocks, evaluation, scripts and tests; TypeScript checks cover components, component tests, browser tests and configuration.

Keep domain data fictional, tool permissions narrow and modes labelled. Add a failing regression test before fixing an approval, cancellation, idempotency or recovery bug. Process tests use actual loopback services on the reserved ports and must run sequentially. Stop your own demo first; never stop an unrelated listener or change ports to hide a collision.

Model work is optional and uses the shared machine lease. Do not add a model download to fixture CI. Preserve frozen manifests; changes need a new reviewed split/version and new hashes, not an overwritten benchmark. Report model failures and missing claim reviews alongside successful results.

Regenerate contracts with `uv run python scripts/export_contracts.py` and `npm --prefix web run contracts`. Include user-visible behavior, validation evidence and relevant limitations in a proposed change. Never commit `.runtime`, weights, private data, credentials or bulk recordings. Original contributions use the repository's MIT licence; third-party models retain their own licences.
