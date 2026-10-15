# Casework Agent v1 specification

Status: approved planning scope; implementation and measurements have not started.

## Product and boundaries

Build a local operations workbench for one fictional delivery exception. An operator opens a case, sees an agent gather evidence through independent order, carrier and ticket HTTP services, reviews an exact proposal, and approves or rejects it. Approval permits a fictional service ticket and a fictional order annotation. The final screen shows confirmed outcomes or an unresolved partial result.

Use Python FastAPI, SQLite and a React/TypeScript/Vite client. The API is `127.0.0.1:8112`, web is `127.0.0.1:5112`, order service is `127.0.0.1:8212`, carrier is `127.0.0.1:8312`, and ticket service is `127.0.0.1:8412`. Each service has its own SQLite file and process. HTTP boundaries, transactions, failures and restarts must be real.

Python is 3.12.x, `requires-python = ">=3.12,<3.13"`, managed through uv. Use Node 24 LTS through an existing local manager; verify availability before selecting it. A documented, tested local exception is allowed if unavailable; CI stays on Node 24. Pin actual resolved dependencies and record versions. Do not replace global runtimes.

No real customers, messages, refunds, payments, external business accounts, production writes, authentication provider, cloud deployment, MCP adapter or general-purpose agent framework in v1. The unauthenticated operator UI is a loopback demonstration, with exact-origin CORS and Origin validation on browser mutations. It must not be exposed as a multi-user service.

## Fixed conservative policy

Every scenario has an immutable UTC `as_of`. Policy `delivery-v1` has a canonical SHA-256 hash and uses only evidence from the current case. Never use the wall clock to decide whether a fixture is overdue.

1. `open_investigation` is permitted only if the order status is `in_transit`, carrier status is `delayed`, the last carrier event is at least 48 hours before `as_of`, the order has no unsupported policy_exception, and the carrier reports neither delivery nor contradictory events.
2. A missing nullable business value, unknown state, inconsistent order/carrier data, unsupported policy_exception, delivered/cancelled order and all other valid evidence cases yield `manual_review`. A structurally invalid HTTP payload or unreadable policy fails gathering with no proposal; do not invent missing evidence.
3. Both actions create one fictional ticket and one order annotation. Neither action promises delivery, compensation, a refund or a customer contact. The bounded draft is an internal note only.
4. Ticket priority is `normal`; `manual_review` uses queue `human_review`, and `open_investigation` uses queue `delivery_investigation`. No other queue or priority is executable.
5. Approval expires 15 minutes after proposal creation using a persisted UTC timestamp and injected clock. Proposal changes or policy changes invalidate approval.

Matthew may optionally supply 5-10 lines explaining an exception threshold, an escalation preference and acceptable internal-note wording. The defaults above remain executable without this contribution. A policy change requires tests, a new policy version/hash, proposal invalidation and a state-file entry.

## Typed contracts

All JSON uses snake_case, UTC RFC3339 timestamps ending in `Z`, bounded strings, UUID identifiers and discriminated enums. Pydantic models reject unknown fields. TypeScript types are generated from the checked-in OpenAPI contract; handwritten UI state types may wrap them. Money and personal data are absent. All bodies are limited to 32 KiB, notes to 2,000 characters, rationale to 1,000, and internal drafts to 500.

| Type | Exact required fields |
| --- | --- |
| `CaseSeed` | `scenario_id: str`, `order_id: str`, `as_of: datetime`, `mode: fixture|model` |
| `Order` | `order_id: str`, `shipment_id: str`, `status: in_transit|delivered|cancelled|unknown`, `version: int >= 1`, `note: str`, `policy_exception: str|null`, `annotations: list[OrderAnnotation]` |
| `Shipment` | `shipment_id: str`, `status: delayed|in_transit|delivered|unknown`, `version: int >= 1`, `last_event_at: datetime|null`, `conflicting_events: bool`, `events: list[CarrierEvent]` |
| `CarrierEvent` | `code: str`, `at: datetime`, `description: str` |
| `Policy` | `version: str`, `hash: str`, `delay_hours: int`, `approval_ttl_seconds: int`, `rules: list[str]` |
| `Evidence` | `id: UUID`, `case_id: UUID`, `source: order|carrier|policy`, `source_id: str`, `source_version: str`, `payload: Order|Shipment|Policy`, `payload_hash: str`, `fetched_at: datetime` |
| `AgentDecision` | `action: open_investigation|manual_review`, `rationale: str`, `draft_note: str`, `evidence_ids: list[UUID]` |
| `TicketIntent` | `kind: create_ticket`, `order_id: str`, `action: Action`, `queue: delivery_investigation|human_review`, `priority: normal`, `internal_note: str` |
| `AnnotationIntent` | `kind: annotate_order`, `order_id: str`, `action: Action`, `ticket_ref: "$ticket"`, `expected_order_version: int` |
| `Proposal` | `id: UUID`, `case_id: UUID`, `version: int`, `policy_hash: str`, `evidence_ids: list[UUID]`, `evidence_hashes: list[str]`, `order_version: int`, `shipment_version: int`, `action: Action`, `rationale: str`, `draft_note: str`, `intents: tuple[TicketIntent, AnnotationIntent]`, `created_at: datetime`, `expires_at: datetime`, `hash: str` |
| `ApprovalRequest` | `proposal_id: UUID`, `proposal_hash: str`, `expected_case_version: int`, `decision: approve|reject` |
| `Approval` | `id: UUID`, `case_id: UUID`, `proposal_id: UUID`, `proposal_hash: str`, `decision: approve|reject`, `actor: "local_operator"`, `created_at: datetime` |
| `Operation` | `id: UUID`, `case_id: UUID`, `approval_id: UUID`, `ordinal: 1|2`, `kind: create_ticket|annotate_order`, `key: str`, `request_json: object|null`, `request_hash: str|null`, `state: pending|in_flight|unknown|succeeded|rejected`, `attempts: int`, `remote_id: str|null`, `response_json: object|null`, `last_error: str|null` |
| `OrderAnnotation` | `annotation_id: UUID`, `ticket_id: UUID`, `action: Action`, `operation_key: str` |
| `Ticket` | `ticket_id: UUID`, `order_id: str`, `action: Action`, `queue: Queue`, `priority: normal`, `internal_note: str`, `operation_key: str` |
| `CaseView` | `id: UUID`, `scenario_id: str`, `order_id: str`, `as_of: datetime`, `mode: fixture|model`, `state: CaseState`, `version: int`, `proposal: Proposal|null`, `evidence: list[Evidence]`, `operations: list[Operation]`, `events: list[AuditEvent]`, `available_actions: list[approve|reject|cancel|repropose|reconcile]`, `error: ApiError|null` |
| `JournalResult` | `key: str`, `request_hash: str`, `outcome: succeeded|rejected`, `http_status: int`, `response_json: object`, `committed_at: datetime` |
| `AuditEvent` | `id: int`, `case_id: UUID`, `kind: str`, `payload: object`, `created_at: datetime` |
| `ApiError` | `code: str`, `message: str`, `retryable: bool`, `case_id: UUID|null`, `request_id: UUID`, `details: object` |

`Action`, `Queue` and `CaseState` are named enums. API failures use `{"error": ApiError}`. Use 400 malformed input, 403 rejected browser origin, 404 missing ID, 409 state/version/key conflict, 422 schema failure, 503 unavailable dependency and 504 bounded read timeout. Errors never embed model stack traces or raw environment configuration. Case creation validates scenario_id/order_id/as_of against the immutable synthetic scenario manifest. available_actions is computed from persisted state, operation attempts and expiry; UI state alone never establishes permission.

Canonical hashing uses UTF-8 JSON, sorted keys, separators `(',', ':')`, no NaN, stable ISO timestamps and no `hash` field in the object being hashed. Preserve array order. Approval is a local database authorization record, not a cryptographic signature or proof of an authenticated human identity.

## Model and fixture modes

`AgentAdapter.propose(context: AgentContext, tools: ReadTools) -> AgentDecision` is async. `AgentContext` contains `case_id`, `order_id` and `as_of`; `ReadTools` collects the evidence set. `ReadTools.get_order(order_id)`, `get_shipment(shipment_id)` and `get_policy()` return `Evidence`; each validates its identifier against the current case before using a fixed configured HTTP service URL. A model cannot choose a host or arbitrary order.

`FixtureAdapter` is a deterministic baseline, visibly labelled `Fixture workflow`. It follows order -> shipment -> policy, applies the fixed rules and supplies a canned internal draft. Never count this as model inference.

The default `LocalModelAdapter` uses pinned `mlx-community/Qwen3-14B-4bit` through project-local MLX LM and Outlines on Apple Silicon. The original specification selected `Qwen/Qwen2.5-1.5B-Instruct`; its failed evaluation and immutable snapshot remain preserved as the v1 baseline. The explicit model repair selects Qwen3 after development comparisons. [MODEL-CONFIG](MODEL-CONFIG.md) records the current revision, runtime, separate Apache-2.0 model terms and comparison profiles. [MLX LM](https://github.com/ml-explore/mlx-lm) supplies local loading/generation.

Preparation selects a named public model profile at its pinned immutable revision. Download safetensors, configuration, tokenizer, chat-template, model-card and available licence files with token=False into `.runtime/models/<checkpoint>/<revision>` using a project-local cache, then record file hashes and terms. Do not load pickle weights or enable trust_remote_code. Dependencies remain locked. Public download and local inference require no cloud credentials or paid resources.

The model-session helper acquires the machine lease before loading any weights and starts an owned subprocess with inherited pipes for typed JSON-line requests/responses. The child calls MLX LM load on the exact local snapshot, applies its checkpoint-provided chat template once with thinking disabled, and uses bounded schema-constrained generation with temperature 0 and max_tokens 768. The schema permits only unread scoped tools until all evidence is fetched, then binds actual citation IDs while leaving both actions available. Compact context copies observed fields and calculates elapsed hours without supplying an action. An incorrect policy choice fails immediately with no repair feedback. No TCP model port or resident server is needed. A schema/tool-selection smoke probe is required before evaluation. Enforce an 8,192-token prompt limit and 120-second per-case deadline outside the child; terminate an unresponsive owned child. Confirm its exit before releasing the lease. Failed download, unavailable runtime or failed compatibility probe is reported precisely; fixture work continues, with no silent model substitution.

Prompt the model to emit exactly one JSON object: `{"kind":"tool","name":"get_order|get_shipment|get_policy","arguments":{...}}` or `{"kind":"proposal","decision":AgentDecision}`. Pass a schema appropriate to the current evidence state to the decoder and include its JSON in the worker prompt. This is a model-driven tool loop using schema-validated JSON, not a claim of native function-calling support. Each tool's result is appended as a delimited untrusted-data message. Validate every JSON object with discriminated Pydantic models before dispatch; do not strip arbitrary markdown or execute model text. Store the assistant/tool exchange, timings and parsed decisions. Reject arbitrary tools, out-of-case IDs, malformed arguments and unsupported evidence references; one bounded protocol correction is available, while a policy mismatch fails immediately.

Bound a run to 8 assistant turns, 8 read calls, one schema repair and 120 seconds total. Set an output token limit of 768; record tokenizer-counted input/output tokens when available and otherwise `null`, not zero. Each read has a 2-second timeout, at most 3 attempts with 100/300 ms backoff. The final decision must cite order, carrier and policy evidence from this run. Deterministic code checks the selected action against policy and compiles both write intents. Model text never becomes an executable URL, method, queue, priority or write payload field beyond the bounded internal note.

The app's model case opens an owned ModelSession, acquires the lease, loads once, runs its tool loop, then exits the child and releases. A busy lease returns `model_busy` without loading. A benchmark instead owns one ModelSession for the entire run and injects its ModelClient into an evaluation app/worker running on the same event loop, while all business service requests still cross actual HTTP. The three mocks remain separate processes. Do not reacquire the same lease inside a borrowed session. If the model exceeds budgets or fails validation, record a specific failure without switching modes. Only an actual access/runtime/probe/evaluation failure can block real-model acceptance; a missing user model choice is not a prerequisite.

## State machine and approval protocol

`new -> gathering -> needs_approval -> approved -> executing -> completed` is the success path. `gathering -> failed` is allowed before a proposal. `needs_approval -> rejected` records a human rejection. `new|gathering|needs_approval|approved -> cancelled` is allowed only before any operation is claimed. `needs_approval|approved -> stale` records expired/changed evidence or policy. `executing -> review_required` covers partial or unresolved writes. `failed|stale|rejected -> gathering` is allowed only through explicit repropose, with no operation ever sent (all attempts must be zero). A definitive rejection of a sent operation remains auditable and cannot be reproposed within that case. Terminal cases otherwise do not restart implicitly.

Every mutation increments `cases.version` in a SQLite transaction and appends an audit event in the same transaction. Proposal versions increase monotonically; old proposals and approvals remain immutable. Recovery may move review_required back to executing and then completed when journal evidence resolves uncertainty; it never grants new authority. On worker takeover, an interrupted gathering run becomes failed with agent_interrupted and can be explicitly reproposed; do not leave a permanent spinner or silently repeat an expensive model run. An approval request must carry `Idempotency-Key`, the exact proposal ID/hash and the UI's expected case version. Replaying the same key/body returns the original response even when the case version has since changed; reusing a key with a different body returns 409.

Before approval, fetch order and carrier versions outside the local transaction. A failed fresh read leaves the proposal pending and returns a dependency error; missing data is not evidence that versions match. Inside `BEGIN IMMEDIATE`, re-read case version/state/proposal and policy hash, check expiry, match the fetched source versions and proposal hash, then insert approval and two operation rows atomically. A mismatch marks the proposal stale, returns 409 and creates no executable operations. Rejection records no operations. Approval is durable before the HTTP response returns.

The worker repeats the fresh-read checks immediately before claiming operation 1. The claim is a transaction that checks the approval/hash, policy, expiry, state and no cancellation, materializes the exact request body, increments attempt count and sets the operation `in_flight` plus case `executing` before sending HTTP. This first claim locks authorization for both approved intents. Later expiry does not invalidate reconciliation or the dependent annotation under its saved precondition; neither may change the approved body.

The system does not provide an atomic snapshot across independent services. A carrier update can arrive after the final preflight read. Record validation timestamps; do not claim that all approved evidence stays current during execution. Order annotation uses the approved order version as a remote compare-and-swap precondition. A subsequent order change yields a partial-result review if a ticket already exists.

Operation 1 key is `cw:<case_id>:<proposal_version>:ticket`; operation 2 key is `cw:<case_id>:<proposal_version>:annotation`. Operation 2 remains `pending` with null request/hash until operation 1 is confirmed. Then resolve its only dynamic field, `$ticket`, to the persisted confirmed ticket ID and persist the complete request/hash before sending. No other field may be recomputed from model output or fresh evidence.

Cancellation and first-operation claim race on `BEGIN IMMEDIATE`: whichever commits first wins. Once any operation is in_flight, unknown or succeeded, cancellation returns 409 `execution_started`, performs no compensation and shows the current confirmed/unknown outcome. UI copy is `Cancel before execution` while available, and `Execution started; reconciliation may still be required` afterwards.

## Remote idempotency and recovery

Order and ticket services each have a separate atomic idempotency journal. On POST, inside one SQLite transaction: look up key; replay stored status/body if its request hash matches; return 409 for a different hash; otherwise validate domain preconditions, write the domain row and journal result, then commit. Check for an existing key before checking the current order version. Keys are never reused for a changed payload. These local mocks retain journal entries for the entire database lifetime.

Expose `GET /v1/operations/{key}` returning JournalResult or 404. Definitive domain rejections are journaled with outcome rejected; malformed requests and key conflicts do not overwrite an existing entry. A configured fault may drop the connection after commit. The caller treats a timeout, connection loss or 5xx after a mutation as `unknown`, never as proof that the operation did not happen. Persist that status and stop later operations.

On worker takeover, treat leftover `in_flight` as `unknown`. Reconciliation queries the same remote service and key. A matching committed success becomes `succeeded`; a matching committed rejection becomes `rejected` and follows the definitive-rejection rule below. A different hash becomes `review_required` with no new write. A 404 is an observation, not proof that a delayed request cannot arrive: an identical same-key replay is safe only because the mock service serializes its idempotency journal with the mutation. Never create a replacement key. If the remote cannot be reached, keep `unknown` and display `Outcome unconfirmed`.

At most 3 mutation sends per operation, including the initial send. Each has a 3-second timeout. Reconciliation performs at most 3 status reads per operator request with 100/300 ms backoff. After the budget, set case `review_required`; explicit `reconcile` may repeat bounded status reads and may replay the identical request only if the remaining persisted send budget permits. If the status confirms success, finish the dependent annotation under its saved precondition. A definitive precondition rejection sets the operation `rejected` and case `review_required` if any earlier action succeeded, otherwise `stale`. No automatic compensation, deletes or new proposal follows a partial result.

Use one worker process per application database plus a database worker lease (`owner_id`, PID, acquired/heartbeat timestamps) to detect a second live worker. A claim includes an incrementing generation; stale owners cannot update local results. Remote same-key deduplication remains required because a fenced worker might already have sent HTTP. The lease expires after 30 seconds without a heartbeat, refreshed every 5 seconds. On takeover, reconcile all incomplete operations before claiming new ones. Never equate a reused PID with an owned process.

The guarantee is durable local authorization plus at-most-one domain side effect per key in each mock's transaction. There is no distributed exactly-once guarantee and no cross-service rollback. Both an incomplete pair and an unknown outcome must remain visible and auditable.

## Storage

Use `sqlite3`, parameterized statements, foreign keys enabled on every connection, WAL mode, 5-second busy timeout and explicit versioned migrations. Migrations run before the worker; a failed migration prevents startup. JSON columns store validated canonical JSON.

| Database/table | Required columns and constraints |
| --- | --- |
| app `schema_migrations` | `version INTEGER PRIMARY KEY`, `applied_at TEXT` |
| app `cases` | `id TEXT PK`, scenario/order/as_of/mode/state, `version INTEGER`, `reconcile_requested INTEGER DEFAULT 0`, created/updated timestamps; mode/state CHECK constraints |
| app `evidence` | `id TEXT PK`, `case_id FK`, source/source_id/source_version/payload_json/payload_hash/fetched_at |
| app `proposals` | `id TEXT PK`, `case_id FK`, version/payload_json/hash/created_at/expires_at; UNIQUE(case_id,version) |
| app `approvals` | `id TEXT PK`, `case_id FK`, `proposal_id FK`, hash/decision/actor/created_at; UNIQUE(proposal_id) |
| app `operations` | contract columns plus `worker_generation INTEGER`, updated_at; UNIQUE(case_id,ordinal), UNIQUE(key); one execution per case |
| app `audit_events` | `id INTEGER PK AUTOINCREMENT`, `case_id FK`, kind/payload_json/created_at |
| app `api_idempotency` | `key TEXT PK`, route/body_hash/status/response_json/created_at; route included in fingerprint |
| app `agent_runs` | `id TEXT PK`, `case_id FK`, adapter/model/config_hash/status/trace_json/started_at/finished_at; null usage allowed |
| app `worker_lease` | `singleton INTEGER PK CHECK(singleton=1)`, owner_id/pid/generation/heartbeat_at/acquired_at |
| orders `orders`, `annotations` | validated order fields; annotation ID PK, order FK, ticket_id/action/operation_key UNIQUE; order version increments once |
| carrier `shipments`, `events` | validated shipment fields; event ID PK and shipment FK; seeded versions |
| orders/tickets `idempotency` | key PK, request_hash, status, response_json, committed_at; written with domain side effect |
| tickets `tickets` | ticket contract fields; ticket_id PK, operation_key UNIQUE |
| each mock `schema_migrations` | version PK, applied_at |

Reproposal is permitted only before any operation rows have been created, except an approved case invalidated before claim: remove its unclaimed pending operation rows within the invalidation transaction while retaining the approval/audit history. Never delete a row that was sent. The UNIQUE(case_id,ordinal) constraint deliberately prevents executing a second proposal for an already-executed case. A reconcile request sets cases.reconcile_requested in the same transaction as its audit event and API replay response; the single worker claims and clears the flag transactionally, performs the bounded check and persists its result. Unknown outcomes remain review_required until confirmed; an explicit request grants no new write authority.

## HTTP surface

| Service / endpoint | Contract |
| --- | --- |
| app `GET /health` | readiness, schema version, mode availability, worker status; no secrets |
| app `GET /v1/scenarios` | synthetic scenario summaries with expected action excluded from the UI response |
| app `POST /v1/cases` | CaseSeed + Idempotency-Key -> 201 CaseView; worker gathers asynchronously |
| app `GET /v1/cases`, `GET /v1/cases/{id}` | case summaries / CaseView; UI polls active case every 1 second |
| app `POST /v1/cases/{id}/decisions` | ApprovalRequest + Idempotency-Key -> CaseView or precise 409 |
| app `POST /v1/cases/{id}/cancel` | expected_case_version + Idempotency-Key -> CaseView or execution_started |
| app `POST /v1/cases/{id}/repropose` | expected_case_version + Idempotency-Key -> gathering, with new proposal version |
| app `POST /v1/cases/{id}/reconcile` | expected_case_version + Idempotency-Key -> persisted bounded reconciliation job, 202 CaseView |
| orders `GET /v1/orders/{id}` | Order |
| orders `POST /v1/orders/{id}/annotations` | order_id, action, ticket_id, expected_order_version + Idempotency-Key -> 201 OrderAnnotation |
| carrier `GET /v1/shipments/{id}` | Shipment |
| tickets `POST /v1/tickets` | TicketIntent without kind + Idempotency-Key -> 201 Ticket |
| tickets `GET /v1/tickets/{id}` | Ticket |
| orders/tickets `GET /v1/operations/{key}` | committed response envelope and hash, or 404 |

Mutation endpoints require JSON and idempotency keys of 1-160 ASCII characters. Test fault controls are constructor configuration and local fixture files, never an exposed production-like reset endpoint. Enforce loopback binding; test clients may omit Origin, while supplied browser Origin must equal `http://127.0.0.1:5112`.

## UI system

Build a calm operational workbench: scenario/inbox column, active case evidence and timeline, proposal/approval panel. Use system sans-serif typography, 14px body/20px line-height, 12px labels, 24px page title; monospace only for IDs. Spacing scale is 4, 8, 12, 16, 24, 32px. Panels use 1px borders, 10px radius and restrained shadows.

Light colors: background `#F5F7FA`, surface `#FFFFFF`, text `#162033`, secondary `#475569`, border `#CBD5E1`, action `#1D4ED8`, positive `#166534`, warning `#92400E`, danger `#B91C1C`. Dark colors: background `#0B1220`, surface `#162033`, text `#F1F5F9`, secondary `#CBD5E1`, border `#475569`, action `#93C5FD`, positive `#86EFAC`, warning `#FCD34D`, danger `#FCA5A5`. Check contrast in implementation; status always includes text/icon. Theme defaults to system and supports persisted explicit light/dark selection.

At >=1100px use 260px inbox plus flexible evidence plus 360px proposal. At 720-1099px use inbox plus stacked evidence/proposal; below 720px use one column with scenario selection above case content. Long IDs wrap; tables have labelled horizontal scroll containers. No fixed-height content that hides a proposal.

Use semantic landmarks/headings, labelled buttons, visible 2px focus rings, 44px action targets, keyboard-operable controls, an aria-live polite summary for state changes and focus transfer to a newly loaded case heading. Approval is an explicit button, with displayed action, internal note, evidence versions and expiry. Disable while pending; transport failure preserves input and permits same-key retry. A changed proposal visibly invalidates the old approval controls. Cancel uses the protocol's exact availability. Unknown outcome and partial success show each operation separately.

Transitions are 120ms opacity/color for status changes, with no perpetual decoration or moving timelines. Respect prefers-reduced-motion. Include empty, loading, model unavailable, validation failure, rejected, stale, cancelled, completed, partial and unknown states. The mode badge remains visible on every case and report.

## File boundaries

`src/casework_agent/` holds `config.py`, `contracts.py`, `clock.py`, `hashing.py`, `db.py`, `repository.py`, `policy.py`, `tools.py`, `agent.py`, `model_adapter.py`, `model_worker.py`, `model_session.py`, `workflow.py`, `executor.py`, `recovery.py`, `worker.py`, `api.py`, `cli.py` and migrations. `mocks/` holds separately runnable `orders.py`, `carrier.py`, `tickets.py`, plus shared contracts/storage/faults; no direct app-to-mock database reads. `fixtures/` holds synthetic scenarios and development/holdout manifests. `eval/` holds runner, scoring and report schemas. `scripts/` holds local lifecycle, snapshot/session CLI and contract generation. `web/src/` holds generated API types, typed API client, app shell, case/inbox/evidence/proposal/timeline components and theme styles. Tests live in `tests/unit`, `tests/integration`, `tests/e2e`, `web/src/**/*.test.tsx` and `web/e2e`.

## Acceptance and evidence

Fixture acceptance requires the complete browser flow through actual local services, restart/failure matrix, zero unapproved writes and zero duplicate side effects in that matrix, all strict checks including tests, and honest fixture labels. Real-model acceptance additionally requires the configured local adapter, traceable held-out evaluation and manual review of claims; a missing model is recorded as a blocked evidence gate. See EVALUATION.md and the task plan for exact counts and gates. No results are prefilled.

Runbooks must record owned PIDs and exact commands, stop only owned processes, fail on occupied reserved ports and never use a broad kill. All heavy model loads/evaluation acquire `/tmp/bentolabs-portfolio-ml.lock` atomically with mkdir before loading weights, record owner/project/PID/start/purpose/nonce, unload or confirm owned server exit, and only then release their own matching lease in finally/trap. If cleanup fails, retain the lease and report the live process. A busy lease means continue light work; do not spin, delete it or substitute fixture results.
