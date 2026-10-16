# Engineering decisions

Casework Agent separates proposed actions from the authority to execute them. The model reads evidence and proposes; deterministic code validates policy, records exact approval and compiles the permitted writes.

## Persistence and worker ownership

SQLite stores validated contracts as JSON, with indexed columns for identities, states, versions, operation keys and relationships. This keeps the application small while making approval and execution transitions transactional. Ad hoc analytics require extracting fields from JSON.

One asynchronous worker runs inside the API process, alongside a separate heartbeat task. A durable lease and monotonically increasing generation fence stale workers. API and worker availability are coupled; saved state and generation checks support recovery after restart.

Gathering runs also persist an ID, owner and generation. Late evidence, success, failure and trace writes cannot overwrite a replacement run. Explicit reproposal queues a case as `new` before the worker starts `gathering`.

## Approval and execution

Approval binds an immutable proposal to its cited evidence hashes, source versions, policy and expiry. The first execution claim arbitrates with cancellation in one transaction. The executor persists an operation key, payload and hash before HTTP, then treats an ambiguous result as unknown.

Each fictional service commits its domain change and idempotency journal together. Reconciliation confirms the saved key and hash or replays the identical request within a persisted three-send budget. This provides per-key duplicate protection in the simulation. There is no cross-service rollback or distributed exactly-once guarantee.

## Bounded integrations

Dependency responses stream under a 32 KiB cap with total deadlines: two seconds for evidence reads, three seconds for writes and journal reads. The local integration contract accepts identity encoding only; compressed responses fail explicitly. The model's complete tool loop, including awaited reads, has a 120-second deadline.

The browser retains the highest observed version per case and ignores superseded selections. Its small inbox cache lasts for the page's lifetime. Failed mutations preserve their original request body and idempotency key for explicit retry.

## Runtime and verification

Python 3.12 and Node.js 24 LTS are the supported toolchain, verified in Ubuntu CI. TypeScript 5.9.3 matches the supported peer range of openapi-typescript 7. Benchmark-specific runtimes and hardware are recorded in [MODEL-CONFIG](MODEL-CONFIG.md).

The lifecycle helper supports tracked detached services for development and a foreground supervisor for browser tests. Process identities include PID, start time, command arguments and an ownership nonce. The supervisor defers its interruption handler during spawn and registration while leaving child termination signals unblocked.

Python temporary data and browser databases stay under the repository's ignored `.runtime` directory. Port-owning suites run sequentially. A fresh checkout creates its temporary parent explicitly before fixture initialization.

## Review history

The initial review of `d6aa779..009b67e` identified six important findings. The resulting changes included:

1. Cited evidence could be older than the cached source used for authorization. The failing regression now rejects superseded citations. Publication derives policy, versions and intents from the validated cited snapshot and aligns each hash with its evidence ID.
2. A superseded gathering run could publish or fail a replacement run. Migration 2 persists run ID, owner and generation. Success, failure and trace writes check that identity plus the current lease in their transaction. Regression covers late success, late failure, aligned hashes and a former worker taking ownership again.
3. Creation accepted arbitrary scenario IDs, orders and business timestamps. The API now admits only the exact tuple supplied by its configured fictional scenario. Three failing API cases now reject each mismatch before storage.
4. Expiry hid approval without exposing renewal. The worker transactionally marks expired unclaimed proposals stale. Python and browser checks now renew without cancellation or writes.
5. Fresh-checkout pytest lacked the ignored temporary parent. The clean archive initially produced 37 FileNotFoundError fixture errors. `tests/conftest.py` now creates only this project's `.runtime` before temporary fixture initialization. Clean-checkout verification is recorded in STATE.
6. Existing browser replay covered server idempotency, not the UI's lost-response behavior. The new test forwards the real approval to the API, waits for its committed response, then aborts only its delivery to the browser. Retry saved request uses the identical body/key; one ticket/annotation pair remains. No business response or state is fabricated.

Evidence, ownership, admission and expiry regressions were observed failing before their fixes. The browser response-loss test strengthened coverage of existing retry behavior. Source `1da911f` passed the recorded clean-checkout checks.

A subsequent whole-project review at `92534bb` identified six further issues involving remote confirmations, network bounds, browser response ordering, startup cleanup, lease acquisition and carrier chronology. All were fixed in `33c3efa` and checked through focused follow-up. The [review record](REVIEW-2026-10-15.md) contains the findings and regression evidence; [STATE](STATE.md) links successful CI runs.

## Remaining limitations

The original Qwen2.5 1.5B model failed its published quality thresholds at source `1da911f`. Those reports remain frozen. The [model repair](MODEL-ITERATION.md) uses development-only candidate comparisons, Qwen3 14B, schema-constrained output and explicit factual context. Deterministic code validates the model's action without giving policy-answer feedback. Fresh evaluation uses a separately authored, frozen challenge after the inference source and prompt freeze.

Human factual-claim review and manual screen-reader testing remain pending. The application has no public authentication, tenant isolation or production validation. Independent review examined the code; execution evidence comes from recorded local checks and GitHub CI.

## V4 explanation boundary

Exact integer policy-relative age and generic UTC relations remove floating-point rounding and same-zone daylight-saving ambiguity. Qwen still selects between both actions over these computed features. The application validates scope, evidence and action before producing a proposal, with no wrong-action replacement or feedback.

Development exposed correct actions accompanied by false intermediate assessments. Strictly blocking those redundant assertions reduced workflow availability; a smaller action-only experiment also failed. The versioned guarded-deliberation protocol therefore preserves intermediate generation and records its errors, but derives the displayed policy explanation independently from raw evidence. This fixes the output authority boundary; it does not establish that Qwen's reasoning is correct or improve its historical trace scores. The original broader factual-review gate is retained. See [repair evidence](MODEL-REPAIR-V4.md).
