# V5: model-generated condition correctness

Approved scope: repair the missing-timezone decision and incorrect intermediate claims, then measure a separately authored fresh set. Preserve every earlier report and input. Native implementation; no model, sampling, business-policy or approval/recovery changes.

## Design and acceptance

The working hypothesis is interference between jointly generated conditions. Exposed captured-input probes isolate each condition in a fresh context with its own fixed rule and only its existing CHECK_INPUTS group. The last request sees the six unmodified model booleans and actual citation IDs. Both Boolean values, both actions and all seven reasons remain possible; no oracle, expected label, validator correction or semantic retry enters a prompt.

After the final model response, independently validate all six claims, the reason, action, citations and evidence. Any semantic error fails once, before proposal publication. Code continues rendering factual prospective prose. This restores claim correctness as a requirement instead of allowing a correct action to hide a wrong intermediate claim.

Three scoped model-selected reads, six condition requests and one decision require ten normal inference calls. Allow one global syntax repair (eleven maximum), eight business-tool calls maximum, 120 seconds for the whole case. JSON-line worker calls remain sequential. Record exact per-request phase/field, ordinal, messages, schema/hash, raw reply, usage, duration, repair identity and failure; retain partial traces. The legacy exchange contains read history only, never an invented flattened conversation.

## Execution

1. Preserve exposed probes and document their limited replay scope. Write failing regressions for rejected false claims and unsupported reasons; implement isolated requests and trace persistence.
2. Migrate scripted clients and schema tests. Add isolation, unmodified output, bounded global repair, timeout/partial trace and worker-continuation coverage. Run strict Python and web checks, full pytest and real-service browser recovery.
3. Review independently. Commit clean runtime source, then evaluate all 53 exposed development cases (23 earlier development + 30 published v4 cases) with actual Qwen and a separately labelled fixture comparison. Do not inspect the private v5 challenge.
4. Freeze source, all stage instructions/schemas, pinned model/configuration and existing evidence hashes. Only then open/promote the sealed 30-case challenge and its pre-authored labels, oracles and provenance. Run actual Qwen first, fixture comparison second. No tuning against these results.
5. Report action/outcome/completion counts plus every first-attempt Boolean and supported reason, including failed cases. Target 180/180 correct fields, 30/30 supported reasons/actions/outcomes and 24/24 authorized completions, with zero unapproved or duplicate effects. Human factual review remains distinct and pending.
6. Update public documentation with measured evidence and limitations. Audit tracked/publication contents, scoped commits and authorized ordinary push; verify remote and CI, restore the existing owned demo without clearing its databases.
