# Changelog

## Unreleased

- Revised the README and contributor documentation for a public technical audience, with supported runtime requirements separated from benchmark provenance.
- Removed workstation-specific setup language, transient process IDs and chat-specific handoff instructions from maintained guidance.

## Reliability improvements - 2026-10-15

- Required explicit remote IDs before confirming writes; malformed confirmations stay unknown and recover through the existing journal key.
- Bounded streamed dependency responses and total request/model tool-loop deadlines.
- Protected case selection, inbox and active state against delayed responses; preserved exact mutation retries across selections.
- Cleaned up owned services after interrupted startup and made model lease acquisition failure atomic.
- Escalated contradictory carrier timestamps to manual review.
- Added focused regressions, portable contributor guidance and the pre-publication review record.

## 0.1.0 - 2026-10-15

- Added the fictional delivery workbench, three independent HTTP services and durable SQLite audit records.
- Added immutable proposals, exact approvals, cancellation arbitration, fenced execution and journal recovery.
- Added a bounded local Qwen/MLX subprocess path, separate fixture mode and frozen synthetic evaluation.
- Added strict checks, real-service browser tests, operational guidance and measured evidence.
- Model-quality results and manual accessibility limitations are recorded in [ACCEPTANCE](docs/ACCEPTANCE.md).
