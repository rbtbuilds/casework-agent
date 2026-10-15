# Execution decisions and final review

The approved ten-task plan was implemented natively in this child. A single fresh judgment reviewer examined `d6aa779..009b67e`; there was no per-task agent cascade or second review. Its verdict was With fixes, with no Critical findings, six Important findings and no deferred Minor findings.

## Important findings and fixes

1. Cited evidence could be older than the cached source used for authorization. The failing regression now rejects superseded citations. Publication derives policy, versions and intents from the validated cited snapshot and aligns each hash with its evidence ID.
2. A superseded gathering run could publish or fail a replacement run. Migration2 persists run ID, owner and generation. Success, failure and trace writes check that identity plus the current lease in their transaction. Regression covers late success, late failure, aligned hashes and a former worker taking ownership again.
3. Creation accepted arbitrary scenario IDs, orders and business timestamps. The API now admits only the exact tuple supplied by its configured fictional scenario. Three failing API cases now reject each mismatch before storage.
4. Expiry hid approval without exposing renewal. The worker transactionally marks expired unclaimed proposals stale. Python and browser checks now renew without cancellation or writes.
5. Fresh-checkout pytest lacked the ignored temporary parent. The clean archive initially produced37FileNotFoundError fixture errors. `tests/conftest.py` now creates only this project's `.runtime` before temporary fixture initialization. Clean-checkout verification is recorded in STATE.
6. Existing browser replay covered server idempotency, not the UI's lost-response behavior. The new test forwards the real approval to the API, waits for its committed response, then aborts only its delivery to the browser. Retry saved request uses the identical body/key; one ticket/annotation pair remains. No business response or state is fabricated.

The evidence, ownership, admission and expiry regressions were observed failing before their fixes. Browser retry was a verification gap in existing behavior; its added real-response-loss test passes. Final whole-suite and clean-checkout evidence follows in STATE. No model prompt was tuned against holdout answers.

## Rulings during execution

- Use Matthew's assigned independent child repository instead of creating another worktree. Its working directory/Git root were verified. Cost if wrong: less branch isolation; sibling roots remain untouched.
- Keep pytest temporary data under this child because default shared housekeeping touched other projects' temporary roots and emitted warnings. Cost: fresh checkout needs explicit temporary-parent bootstrap, now fixed and verified.
- Keep one asynchronous worker and separate heartbeat task inside the API process, with a durable lease and generation fencing. Cost: API and worker availability are coupled.
- Use tested local Node26.7.0; CI targetsNode24. Pin TypeScript5.9.3 to openapi-typescript7's supported peer range. Cost: the local run does not establish Node24 CI success.
- Use a foreground lifecycle supervisor and unique browser databases for Playwright; detached developer start retains a tracked owner record. Run port-owning suites sequentially. Cost: additional lifecycle code and serialized process tests.
- Explicit reproposal queues `new` before the worker changes it to `gathering`. Cost: one short observable queue state instead of immediate gathering; no extra executor is launched.
- Store full validated contracts in JSON, with indexed SQLite columns for identities, states, versions, keys and relationships. Cost: less convenient ad hoc SQL analytics.

## Reviewer boundaries resolved

- Keep Qwen's measured failure; quality remediation is outside this fixed-checkpoint implementation and must not tune against this holdout. Cost: the selected model is not useful at v1's required protocol.
- Human claims review and manual screen-reader testing remain pending. Cost: unsupported model claims cannot be certified zero and assistive-technology behavior is not fully verified.
- Distributed exactly-once behavior, cross-service rollback and public authentication remain outside the local simulation. Cost: these guarantees are absent; do not expose it as a production service.
- The reviewer did not rerun real HTTP/browser/model/strict checks. The executor owns those commands and the evidence. Cost: execution evidence is author-produced, with independent code review rather than an independent test run.
- The new evidence regression was outside the review commit range. It was included in the executor's fix pass and full suite. Cost: that test has no second reviewer; no rereview was dispatched.

No Minor findings were deferred. Branch integration remains local; no merge, publication, push or deployment was requested.
