# Case study: evidence before a fictional operations action

An operations agent can produce a persuasive answer while leaving a business system in an uncertain state. This project focuses on the boundary between a proposed resolution, the operator's exact approval and independently committed effects.

The intended user is an operator reviewing delayed deliveries. The local simulation replaces a manual order lookup, carrier lookup, policy check, ticket creation and order annotation. It measures engineering behavior; no customer pilot or time saving is claimed.

The application uses FastAPI/SQLite, a React workbench and three real HTTP service processes. Order/carrier/policy evidence is captured before an immutable proposal appears. An approval binds its hash, source versions, policy and expiry. A fenced worker saves an operation before sending it and asks the remote journal about an uncertain response. The second write substitutes only the confirmed ticket ID and uses the approved order version.

The decisive failure experiment drops a response after the service commits. Treating this as a failed write would invite a duplicate. Here the local outcome becomes unknown, then a matching journal confirms the saved key/hash. The complete browser test drops both responses and still observes exactly one ticket and one annotation. A separate version-conflict test leaves a confirmed ticket with a rejected annotation and review_required state. There is no fabricated rollback.

The fixed-policy baseline achieved30/30correct held-out actions,30/30expected workflow outcomes and24/24authorised completions. Six stale approvals correctly created no effects. The selected local Qwen1.5B checkpoint achieved0/30valid actions and0/24completions: its outputs failed the JSON/evidence protocol. All invalid runs stopped before writes. Raw failures, split hashes and measured usage are retained.

That result supports a narrow conclusion: the deterministic execution boundary contained this model's invalid outputs in these synthetic cases. It does not establish useful model reasoning, general injection resistance or production safety. A future model iteration should use development cases and a newly reviewed evaluation protocol; the failed holdout must not become a tuning set disguised as new evidence.

The workbench was checked in light/dark themes at desktop/mobile widths, with keyboard approval and automated accessibility checks. Manual screen-reader testing is still missing. All integrations remain fictional, loopback-only and single-operator. The public repository/deployment decision has not been authorised.
