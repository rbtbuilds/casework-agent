# Verified failure matrix

The integration tests launch actual order/carrier/ticket processes with separate SQLite databases on ports 8212/8312/8412. Application restart tests additionally launch port 8112. Faults are constructor flags or owned fixture reseeds; no public reset route exists.

| Boundary | Test / observation |
| --- | --- |
| Exact approval replay and changed body | `test_exact_approval_replay_and_changed_hash`; original response replays, changed key body returns409 |
| Wrong hash/version, expiry, policy, changed order/carrier | `test_approval_invalidations_and_rejection`; no operation rows or writes |
| Rejection and explicit reproposal | Same test; new immutable proposal version2, no writes |
| Cancel commits before claim | `test_cancel_wins_before_claim_and_second_worker_is_fenced`; zero writes |
| Cancel after execution starts | `test_drop_after_ticket_commit_recovers_once`;409 execution_started |
| Crash before network send | `test_worker_crash_boundaries[before_send]`; takeover queries404 then same-key replay |
| Crash after ticket commit | `test_worker_crash_boundaries[ticket_committed_before_local_result]`; one ticket and annotation after recovery |
| Crash after annotation commit | Corresponding checkpoint; one pair after recovery |
| Actual app process restart before approval | `test_real_app_process_restart_preserves_pending_approval`; same proposal remains pending, zero writes |
| Interrupted gathering | `test_interrupted_gathering_requires_explicit_reproposal`; failed/agent_interrupted |
| Second live worker and stale generation | Worker tests; second owner cannot claim and old owner cannot save a late result |
| Carrier change before claim | `test_carrier_change_after_approval_prevents_claim`; stale with zero writes |
| Order conflict after ticket | `test_partial_order_conflict_is_not_completed`; ticket succeeded, annotation rejected, review_required |
| Remote outage and explicit reconcile | `test_unknown_outage_explicit_reconcile_and_generation_fence`; outcome stays unknown until same-key recovery |
| Concurrent duplicate remote POSTs | `test_mock_services.py`; one domain effect with matching replay before current-version checks |
| Connection loss after remote commit | Mock and browser tests; journal confirms original result without duplicating either effect |
| Privileged model tool request | `test_model_cannot_dispatch_writes`; rejected before HTTP dispatch |
| Cross-case read | Fixture/tool integration test; rejected before network request |
| Browser retry after successful decision | Playwright repeats saved key/body after completion; original approval response replays |
| Browser changed request on the same key | Playwright receives409; domain counts stay1/1 |

The worker crash checkpoints raise an injected process-death sentinel after durable boundaries and reopen the database under an expired lease. They reproduce storage/network boundaries without claiming an operating-system SIGKILL at every checkpoint. A separate test stops and restarts the actual API process. No cross-service rollback or arbitrary-network exactly-once guarantee is claimed.

Browser evidence covers keyboard approval, 375px/1440px layouts, light/dark themes, reduced motion, zero tested Axe violations and no browser page errors. Manual screen-reader use has not been tested. Full acceptance details and any untested fault edges are recorded in STATE.md and ACCEPTANCE.md.
