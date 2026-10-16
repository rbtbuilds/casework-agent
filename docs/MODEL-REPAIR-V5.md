# V5 model condition repair

V4's first fresh challenge retained a missing-timezone action failure and two incorrect intermediate fields/reasons. The next iteration addresses those generated outputs directly. Independent validation remains mandatory; rejecting a wrong answer is not evidence that the model answered correctly.

## Hypothesis and controlled probe

The v4 context asked Qwen to assess six conditions together, despite supplying separate input groups. Some replies assigned a chronology failure to the carrier-conflict condition or overlooked an unknown timezone. The working hypothesis was interference between conditions in joint generation.

Development replays used only exposed, captured inputs with the same pinned Qwen3 14B snapshot, temperature zero and non-thinking constrained generation. Nine cases produced 54/54 correct fields and nine correct actions/supported reasons; two additional true-conflict controls produced 12/12 correct fields and two correct actions/reasons. A paired four-case replay reproduced both v4 errors with the old prompt, while isolated requests answered both correctly. An eligible control and a true-conflict control were correct in both arms. These probes replay captured observations; they do not exercise HTTP, approvals or recovery, and they are not unseen evaluation evidence.

## Protocol

The model first selects three scoped reads. Each of six subsequent requests starts a fresh context containing one fixed policy condition and only the corresponding fetched-field/computed-fact input group. Both Boolean values remain allowed. No sibling answers, case families, evaluation labels, fault schedules or validator results enter those requests.

A final fresh context contains the six unchanged model Boolean outputs and actual observation IDs. Qwen chooses between both actions and all seven reason labels. It must select investigation only when all six conditions pass, otherwise manual review with a failed condition as the reason. The application does not replace or repair these semantic outputs.

After final generation, code independently checks all six assertions, the chosen reason, action, citations, source scope and evidence revisions. A wrong assertion or unsupported reason fails before proposal publication, even when the chosen action happens to be correct. There is no semantic retry or fixture fallback. Displayed prose remains deterministically rendered from evidence; arithmetic and UTC comparisons are supplied features rather than claims of unaided model calculation.

There are ten normal model requests: three reads, six condition assessments and one decision. One global syntax repair permits at most eleven requests. The complete case retains a 120-second deadline and an eight-tool-call limit. Worker requests remain sequential. Known tokens remain attached to each reply; a failed or cancelled request makes aggregate usage unknown.

## Trace and evaluation contract

`inference_calls` records the actual request boundaries: ordinal, phase, field, repair identity, complete messages, response schema/hash, raw reply, token counts, elapsed time and errors. It preserves partial traces after timeout or malformed output. The legacy `exchange` is explicitly limited to read history; it does not pretend the isolated requests formed one conversation.

Available condition outputs are assessed after the attempt ends, including when the final decision fails. Reports distinguish correct, incorrect and missing/unjudged fields. Missing fields remain in the six-per-case denominator; they are not silently removed or described as false assertions. Supported reasons have a separate all-case denominator. Version 5 adds strict gates for every expected action, outcome and authorized completion; historical minimum thresholds remain separately visible. Machine-checked condition/reason results do not complete the human factual-review gate.

## Measurement sequence

All 53 exposed development cases are evaluated through actual local HTTP integrations, followed by a separately labelled fixture comparison. The separately AI-authored 30-case v5 challenge stays sealed until the implementation, prompts, model settings and evidence identities are frozen. Its first actual-model attempt is retained in full, followed by a same-input fixture comparison. No result-driven changes may turn that challenge into a fresh test again.

The fresh target is 180/180 correct model fields, 30/30 supported reasons/actions/outcomes and 24/24 authorized completions, with zero unapproved or duplicate effects. Published measurements, source identities, failures and remaining limitations belong in [evaluation](../EVALUATION.md) and [STATE](STATE.md). Prior inputs and reports remain unchanged.
