# Browser walkthrough

The main clip demonstrates actual pinned Qwen inference on the exposed delayed-delivery example. The separate recovery clip uses the explicitly labelled deterministic fixture decision and real local HTTP services. Neither clip is unseen model-quality evidence. Approval is automated through the actual browser control; it does not complete human factual review.

| Recording | Mode | Duration | Evidence |
| --- | --- | --- | --- |
| [Main walkthrough](media/casework-qwen.mp4) | Actual Qwen3 14B | 45.76 s | [Browser assertions](evidence/walkthrough-qwen-2026-10-17.json), [uncut WebM](media/casework-qwen.webm), [media hashes](media/casework-qwen.json) |
| [Ambiguous-write recovery](media/casework-recovery.mp4) | Fixture decision, actual HTTP effects | 30.48 s | [Browser assertions](evidence/walkthrough-recovery-2026-10-17.json), [uncut WebM](media/casework-recovery.webm), [media hashes](media/casework-recovery.json) |

Both captures use clean committed source `f6271f9`. The [capture binding](evidence/walkthrough-bindings-2026-10-17.json) records source, modes, model configuration attribution and hashes separately from browser-emitted data. The main case has ten actual model requests and six correct condition answers. The recovery clip retains two uncertainty events and one send per saved operation. Caption timing accounts for video beginning before the test body's clock; the original videos remain available for comparison.

The recorder inspects source records, verifies zero ticket/annotation rows and journal entries before approval, checks the exact proposal ID/hash/case version sent by the browser, then verifies the persisted operations against both actual remote journals and effects. The recovery run drops both write responses after commit. Its durable timeline retains two uncertainty events, then confirms one ticket and one annotation with the same saved keys and one send per operation.

## Record a reproduction

Use Python 3.12, uv, Node 24 and locked dependencies. Install Chromium and prepare/probe the pinned model as described in [RUNBOOK](RUNBOOK.md). Fixture recording requires no model. Rendering requires local FFmpeg with the libx264 encoder and ffprobe. No cloud service or credentials are used.

First inspect `scripts/dev.py status`. Stop a pre-existing owned demo with the lifecycle helper before recording; do not stop an unrelated listener or change reserved ports. The recorder's foreground supervisor stops its own services when the test exits. Each invocation needs a new runtime directory because databases are preserved.

```sh
uv run --no-sync python scripts/dev.py status
uv run --no-sync python scripts/dev.py stop
CASEWORK_RECORDING_MODE=model CASEWORK_BROWSER_ROOT="$PWD/.runtime/record-model-1" PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e -- --config walkthrough.config.ts
uv run --no-sync python scripts/render_walkthrough.py .runtime/record-model-1 .runtime/qwen-walkthrough-1.mp4
CASEWORK_RECORDING_MODE=fixture CASEWORK_BROWSER_ROOT="$PWD/.runtime/record-recovery-1" PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/pw-browsers" npm --prefix web run e2e -- --config walkthrough.config.ts
uv run --no-sync python scripts/render_walkthrough.py .runtime/record-recovery-1 .runtime/recovery-walkthrough-1.mp4
# Restore the original demo only if it was running before these checks:
uv run --no-sync python scripts/dev.py start
```

The standard ModelSession owns the shared ML lease for actual inference. A busy lease fails explicitly before loading; no fixture is substituted. Recording retries are disabled. Failed attempts remain local and are not presented as successful captures.

Each successful recording writes `recording.json`, an uncut `walkthrough.webm`, a completion screenshot and caption PNGs under its ignored runtime root. The renderer adds a 100-pixel caption strip below the original 1440x1000 viewport and exports H.264 MP4 at the original speed with no cuts or synthetic application states. Its JSON sidecar records hashes, measured chapters, mode, source commit/dirty status and codec/duration. Browser and recording test files participate in the strict TypeScript check.

The caption strip explains assertions already checked by the recording. Short-lived remote uncertainty may resolve between browser polls; the recovery clip shows the retained uncertainty events and confirmed effects, rather than manufacturing a paused failure screen. Separate complete process tests exercise restart and unresolved-outcome boundaries.
