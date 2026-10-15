# Model configuration and evidence

The selected profile is **Qwen3 14B, 4-bit**, served locally through MLX. Public checkpoint: `mlx-community/Qwen3-14B-4bit`; immutable revision: `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4`. Preparation downloads approximately 8.3 GB of weights and hashes the selected files, including its embedded tokenizer chat template. Weights remain ignored. The model's Apache-2.0 terms are separate from this project's MIT code licence.

## Generation and validation

The measured runtime uses Python 3.12.14, MLX LM 0.32.0, MLX 0.32.4 and Outlines 1.3.3 on an Apple M5 Pro with 24 GiB memory. Optional model dependencies apply to macOS on Apple Silicon; fixture CI runs without weights on Ubuntu.

Qwen's [14B model card](https://huggingface.co/Qwen/Qwen3-14B) documents the `enable_thinking=False` template option for non-thinking output.

The worker applies the checkpoint's chat template once with `enable_thinking=False` and samples at temperature 0. Consecutive messages from the same role are merged; the final user turn includes the latest evidence, facts and response schema. Content is escaped before rendering so replayed replies, errors and business data cannot insert raw chat-role delimiters. Raw traces remain unchanged. Generation is limited to 768 output tokens and 8,192 prompt tokens. A complete case has eight assistant turns, at most eight reads and a 120-second deadline including awaited tools. One protocol repair is allowed. A policy mismatch fails immediately without answer feedback or a second choice.

Outlines restricts each response to a JSON Schema. Before all evidence is read, the schema permits only unread `get_order`, `get_shipment` and `get_policy` calls with exact scoped identifiers and arguments. The final schema binds citations to the fetched observations and permits both policy actions. Qwen selects the action and generates the rationale and note; deterministic code independently validates the decision before publishing a proposal. See [the model iteration](MODEL-ITERATION.md) for context preparation and development comparisons.

The final context includes copied status/exception/event fields and elapsed hours calculated from the case's `as_of` clock. It contains no oracle action, eligibility answer or evaluation fault. Runtime validation still rejects unknown tools, unexpected arguments, cross-case reads, missing evidence and actions outside policy. The model cannot choose a write URL, method, queue or priority. Its generated note requires exact operator approval.

## Model lifecycle

Preparation selects an explicitly named immutable snapshot. Inference verifies its hashes, acquires the shared machine lease and starts an owned child. The worker runs offline and uses only the project's ignored Outlines cache. It exits before the matching lease is released. Busy models return `model_busy`; there is no automatic substitution or fixture fallback.

A successful probe is bound to the snapshot actually loaded and the protocol version. Changing the selected profile requires another probe before readiness reports it available. Probe success establishes protocol compatibility; evaluation and factual-claim review establish separate quality evidence.

Reports retain exact system instructions, responses, observation IDs, model revisions, file hashes, source/lockfile hashes, usage and timings. Public exports identify the original report hash and their metadata redactions. Warm workflow timings include model/tool work, approval and execution; model loading is recorded separately. They do not measure customer time savings or monetary cost.

## Preserved baseline and comparison profiles

The original **Qwen2.5 1.5B** run used revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, nine hashed files and the original unconstrained JSON protocol. Its [probe](evidence/model-probe.json) omitted required `arguments`. Its [30-case report](evidence/qwen-full.json) recorded 0/30 valid actions and 0/24 completions at source `1da911fb12bb896e750248a67f22345bf3d7892b`. Those frozen reports remain unchanged.

That failed run loaded in 4.136 seconds; failed-case p50 was 4.057 seconds and nearest-rank p95 was 8.055 seconds, with 62,512 input/output tokens across 30 cases. These are failure timings. Initial dirty-tree reports remain under `initial-*.json` for provenance.

`prepare --profile baseline1.5b` selects the original weights with the current protocol; it does not reproduce the old adapter. `prepare --profile qwen7b` selects the development comparison checkpoint `mlx-community/Qwen2.5-7B-Instruct-4bit`, revision `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`. Neither comparison profile is an automatic fallback. The failed 4B comparison remains available as `prepare --profile qwen3-4b`. Restore the default with `prepare --profile qwen3-14b` and rerun the probe.

Use the [runbook](RUNBOOK.md) for commands and [evaluation](../EVALUATION.md) for measured quality and limitations. Human review of generated factual claims remains pending.
