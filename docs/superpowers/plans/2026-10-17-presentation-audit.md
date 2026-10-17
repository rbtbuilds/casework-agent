# Portfolio presentation and evidence audit plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan natively, without a user review checkpoint. Matthew explicitly requested autonomous completion.

**Goal:** Publish a reproducible browser demonstration and a source-grounded audit of retained v5 evidence.

**Architecture:** Keep application and model behavior unchanged. Add recording-only Playwright tests/configuration, a deterministic audit of retained observations/approvals/remote effects, and separate presentation documents. Frozen inputs and reports remain immutable.

**Tech Stack:** Existing Python 3.12, strict TypeScript, Playwright, local Qwen/MLX, FFmpeg.

**Spec:** Matthew's 17 October request; `docs/SPEC.md`, `AGENTS.md`, `docs/RUNBOOK.md`.

## Global constraints

- Own this repository only; use API/web 8112/5112 and services 8212/8312/8412.
- Stop and restore the pre-existing demo through ownership-checked `scripts/dev.py`; preserve databases.
- Actual inference uses the shared ML lease and existing pinned v5 protocol.
- Frozen evidence stays unchanged. Published cases are exposed reproduction inputs.
- Human factual review remains pending; AI-assisted semantic review is labelled separately.
- No model-size search, new application behavior, deployment, paid resources or model uploads.

## Review focus

- A caption must not claim an event that its recording assertions cannot establish.
- Recovery counts must bind the same operation keys and hashes to actual remote journals.
- A passing report must not silently become human factual sign-off.
- Recording output must exclude private paths, owner tokens and machine metadata.
- Tests must run on reserved ports after ownership-checked shutdown, then restore existing data.

### Task 1: Re-audit retained v5 evidence

**Files:** New `scripts/audit_retained_v5.py`, `tests/unit/test_retained_audit.py`, dated evidence JSON and `docs/EVIDENCE-AUDIT-2026-10-17.md`.

- [x] Run the frozen trace and pre-sealed oracle auditors into fresh outputs.
- [x] Add mutation tests for unsupported observations/effects/approval assertions; observe failures before implementing the supplemental auditor.
- [x] Compare retained source payloads, policy, approval hashes, operation bodies/keys and remote effects deterministically; list semantic conclusions separately as AI-assisted review.
- [x] Preserve human fields and frozen bytes; commit the audit and evidence.

### Task 2: Record portable browser demonstrations

**Files:** New `web/walkthrough.config.ts`, `web/walkthrough.spec.ts`, curated videos/recording evidence, `docs/WALKTHROUGH.md`.

- [x] Record one actual-model main flow against clean HTTP services, with evidence inspection, exact approval and zero effects before approval assertions.
- [x] Record one separate fixture flow with both post-commit response drops; verify uncertainty events, remote journals, one send per key and one ticket/annotation pair.
- [x] Save uncut browser video, test-clock diagnostics and machine-readable assertions. Use a permanent mode/workflow caption after the timing review. Export small captioned MP4s with no speed changes.
- [x] Check readable frames, durations, browser errors, public metadata and reproduction commands; commit capture tooling and evidence.

### Task 3: Finish presentation and verification

**Files:** `README.md`, `docs/CASE-STUDY.md`, `docs/RUNBOOK.md`, `EVALUATION.md`, `docs/STATE.md`, `docs/PUBLICATION-AUDIT.md` and new dated verification artifact.

- [x] Lead README with a playable demonstration link and concise current case study; preserve historical reports.
- [x] Run full pytest including startup regression, Ruff, strict Pyright including tests, strict TypeScript, Vitest, build, contract regeneration and all actual-service browser flows including Qwen sequentially.
- [x] Independently review final branch diff and evidence; fix concrete important findings with regressions.
- [x] Restore the original demo and confirm preserved business rows/readiness; record exact checks, limitations and publication scope; make scoped local commits.

Publication: prior explicit repository creation/push authorization remains applicable. Verify scope and public assets before any push; no deployment or release.
