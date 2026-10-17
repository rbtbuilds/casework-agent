# Retained v5 evidence audit

This is a new audit of existing evidence, not a new model evaluation. The 30-case challenge and 53 development cases are public, exposed inputs. Their original reports, model replies, manifests, freezes and human-review fields remain unchanged. No model protocol or application behavior changed for this audit.

## Supported by deterministic comparisons

The frozen independent auditor was rerun on both retained reports: **180/180 challenge conditions and 318/318 development conditions**, **30/30 and 53/53 supported selected reasons/actions**, 830 requests in total, and no trace issues, syntax repairs or replacement answers. The challenge's pre-sealed integer calendar oracles independently agree on all 180 fields. [Challenge recheck](evidence/v5-challenge-trace-recheck-2026-10-17.json), [development recheck](evidence/v5-development-trace-recheck-2026-10-17.json), [oracle comparison](evidence/v5-oracle-recheck-2026-10-17.json).

A supplemental auditor reads the retained per-case databases through read-only SQLite connections. Public JSON exports preserve the fictional business records, observations, proposals, approvals, operations, audit events and remote journals, with source database hashes. They omit worker leases, process records, local paths and application API replay tables. [30-case export](evidence/v5-retained-database-export-2026-10-17.json), [53-case export](evidence/v5-retained-development-export-2026-10-17.json).

For all 83 cases, the new comparisons find no inconsistency between original scenario payloads, observed payload hashes, cited evidence, proposal content hashes and saved proposals. The checks also compare each approved operation with its exact proposal intent, approval identifier/hash, saved request body/hash, deterministic operation key, remote journal and resulting domain row. Both journals and remote effects match, with one send per operation. The dependent annotation names the confirmed ticket and increments the approved order version once. Approval precedes both claims in the retained event sequence.

The 30-case challenge has **24 exact approvals, 24 ticket/annotation pairs and six stale cases with no approvals, operations or remote effects**. The 53-case development report has **47 exact approvals/pairs and six zero-effect stale cases**. [Challenge binding audit](evidence/v5-retained-bindings-2026-10-17.json), [development binding audit](evidence/v5-retained-development-bindings-2026-10-17.json).

These are consistency checks of retained artifacts. A database hash recorded now does not independently prove its historical authenticity or record every network event. The original report hashes, frozen source, saved raw requests and separate browser executions provide complementary provenance.

## Supported by AI-assisted semantic review

The [separate per-case semantic ledger](evidence/v5-semantic-review-2026-10-17.json) covers all 83 displayed rationales and prospective notes. Each investigation explanation states the six independently verified conditions and exact integer age. Each manual-review explanation states an observed blocker: source status, policy exception, terminal/conflicting events, unknown timezone, missing timestamp, inconsistent chronology or below-threshold age. The wording says "one reason" where multiple blockers exist. Notes describe a proposed internal action and require approval; they do not claim that a ticket was already created, a customer contacted or delivery promised.

No unsupported factual statement was identified in that bounded AI-assisted review. This is a semantic assessment by an AI agent, not a deterministic proof of arbitrary prose and not human factual sign-off. Application code renders these explanations; they are not transcripts of Qwen's reasoning. Raw model claims are the six condition answers and selected action/reason, audited separately.

## Unsupported conclusions

- The model improves this fixed policy over deterministic logic: the validator already knows the permitted answer.
- The result establishes general reasoning reliability, production accuracy, customer savings or statistical independence: the cases are small, synthetic and AI-authored.
- Recovery establishes distributed exactly-once execution or cross-service rollback: journals protect each saved key within these mock transactions.
- Automated approval in a recording or benchmark constitutes human review: it exercises the operator workflow only.

These conclusions are not made by the current presentation. Historical v3/v4 model and explanation errors remain disclosed in their unchanged reports and [review history](REVIEW-2026-10-16.md).

## Uncertain or unperformed

Human factual review remains **pending**: `unsupported_claims` is null, `claims_review_complete` false and `claims_review` false in the actual-model reports. No agent review fills those fields. Manual screen-reader testing and production validation remain unperformed. A missing source timezone remains unknown; neither the model nor this audit invents one. Hard process termination can lose in-memory model replies, and local journals cannot establish an atomic cross-service snapshot.

## Reproduce without weights or services

Run from the repository root after `uv sync --locked`. Use fresh output names; auditors refuse to overwrite evidence.

```sh
mkdir -p .runtime
uv run --no-sync python docs/evidence/v5-trace-auditor.py.txt docs/evidence/qwen-v5-challenge.json fixtures/manifests/v5-challenge.json .runtime/v5-trace-audit.json --protocol docs/evidence/qwen-v5-protocol.json
uv run --no-sync python docs/evidence/v5-oracle-comparison.py.txt docs/evidence/qwen-v5-challenge.json .runtime/v5-trace-audit.json .runtime/v5-oracle-audit.json
uv run --no-sync python scripts/audit_retained_v5.py --report docs/evidence/qwen-v5-challenge.json --manifest fixtures/manifests/v5-challenge.json --snapshots docs/evidence/v5-retained-database-export-2026-10-17.json --output .runtime/v5-effects-audit.json
uv run --no-sync python scripts/audit_retained_v5.py --report docs/evidence/qwen-v5-development.json --manifest fixtures/manifests/v5-development.json --snapshots docs/evidence/v5-retained-development-export-2026-10-17.json --output .runtime/v5-development-effects-audit.json
```

The frozen auditor requires an existing `.runtime` output directory; create it with `mkdir -p .runtime` in a fresh checkout. An export can be recaptured from an existing evaluation root with `--capture-runtime .runtime/eval/<run-id>` and a new `--snapshots` path. That optional step reads the original databases without starting services. Public exports allow the comparisons above without the original local runtime.
