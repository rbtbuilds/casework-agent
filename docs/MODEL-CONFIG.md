# Model configuration and evidence

Selected model: `Qwen/Qwen2.5-1.5B-Instruct`, immutable revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. The public snapshot contains nine selected files; each SHA-256 is retained in [snapshot metadata](evidence/snapshot.json). Weights themselves are ignored and were not uploaded. The model's Apache-2.0 terms are separate from this project's MIT code licence.

Measured runtime: Python 3.12.14, MLX LM 0.32.0, MLX 0.32.4, Apple M5 Pro, 24 GiB RAM. Inference uses the tokenizer's chat template, temperature 0, output cap 768 tokens, prompt cap 8,192 tokens, eight assistant turns, eight read calls, one repair and 120 seconds per case. The model communicates through typed JSON lines over pipes with an owned child; this is prompted JSON tool use, not native function calling. The exact system instruction and response trace are retained in the full report.

The model may request only get_order(order_id), get_shipment(shipment_id) and get_policy(). Runtime validation rejects unknown tools, unexpected argument keys, another case's IDs, missing evidence and actions outside policy. A final proposal must cite actual order/carrier/policy IDs from this run. Text never becomes a URL, method, queue or priority. The bounded note is reviewed as part of the immutable human-approved proposal.

The initial compatibility probe loaded the actual weights and returned `{"kind":"tool","name":"get_policy"}`. Missing `arguments` makes that output invalid. See [the actual probe](evidence/model-probe.json). This is a successful runtime load and a failed protocol gate.

The held-out run used one model child and one shared lease for all 30 cases, with real business HTTP processes per case. All 30 failed validation with `invalid_model_output`; no case reached a valid proposal or approval. The model sometimes asserted delay facts before reading any source and supplied no evidence IDs. These raw outputs remain available for review; unsupported factual claims are **not certified zero**. Human review remains pending.

The latest clean-source benchmark loaded in 4.136 seconds. Warm failed-case p50 was 4.057 seconds; nearest-rank p95 was 8.055 seconds across 30 observations. Tokenizer-counted input+output total: 62,512. Service startup/model load are excluded from per-case timing. These are failure timings, not productive throughput; there is no monetary estimate.

The latest report measured clean committed source `1da911fb12bb896e750248a67f22345bf3d7892b`. Initial dirty-tree reports remain under initial-*.json for provenance. No model, prompt or holdout tuning occurred between runs. Full runtime, snapshot, manifest and lock hashes remain in the reports.

Reproduce with the exact commands in [RUNBOOK](RUNBOOK.md). Before any load, acquire the atomic shared lock, retain its owner token and start identity, and release only after child exit. `model_busy` is explicit; no fallback or silent model swap exists.
