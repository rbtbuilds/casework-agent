# Model configuration and evidence

Selected model: `Qwen/Qwen2.5-1.5B-Instruct`, immutable revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. The public snapshot contains nine selected files; each SHA-256 is retained in [snapshot metadata](evidence/snapshot.json). Weights themselves are ignored and were not uploaded. The model's Apache-2.0 terms are separate from this project's MIT code licence.

Measured runtime: Python3.12.14, MLX LM0.32.0, MLX0.32.4, Apple M5 Pro,24GiB RAM. Inference uses the tokenizer's chat template, temperature0, output cap768tokens, prompt cap8192tokens,8assistant turns,8read calls,one repair and120seconds per case. The model communicates through typed JSON lines over pipes with an owned child; this is prompted JSON tool use, not native function calling. The exact system instruction and response trace are retained in the full report.

The model may request only get_order(order_id),get_shipment(shipment_id) and get_policy(). Runtime validation rejects unknown tools, unexpected argument keys, another case's IDs, missing evidence and actions outside policy. A final proposal must cite actual order/carrier/policy IDs from this run. Text never becomes a URL, method, queue or priority. The bounded note is reviewed as part of the immutable human-approved proposal.

The initial compatibility probe loaded the actual weights and returned `{"kind":"tool","name":"get_policy"}`. Missing `arguments` makes that output invalid. See [the actual probe](evidence/model-probe.json). This is a successful runtime load and a failed protocol gate.

The held-out run used one model child and one shared lease for all30cases, with real business HTTP processes per case. All30failed validation with `invalid_model_output`; no case reached a valid proposal or approval. The model sometimes asserted delay facts before reading any source and supplied no evidence IDs. These raw outputs remain available for review; unsupported factual claims are **not certified zero**. Human review remains pending.

The first measured model load took4.277seconds. Warm per-case failed workflow p50 was4.513seconds,p95 nearest-rank5.949seconds across30observations. These are failed-task timings, not productive throughput. Tokenizer-counted total input+output usage was63751tokens. There is no monetary estimate. Per-case timing excludes service startup and model load. Full provenance includes manifest/lock hashes, Git commit and dirty-state flag.

The first evidence run occurred during implementation on a dirty tree, explicitly recorded in its report. Later migration/formatting or recovery fixes do not imply the model was remeasured; use STATE.md for the latest measured checkpoint. Frozen held-out inputs and the model prompt were not tuned against the failed outcomes.

Reproduce with the exact commands in [RUNBOOK](RUNBOOK.md). Before any load, acquire the atomic shared lock, retain its owner token and start identity, and release only after child exit. `model_busy` is explicit; no fallback or silent model swap exists.
