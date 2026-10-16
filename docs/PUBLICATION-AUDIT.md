# Publication audit

Audit date: 2026-10-15. Published source: `d8956e035af8f30f4255a9e39a0182048105dfea` in [rbtbuilds/casework-agent](https://github.com/rbtbuilds/casework-agent).

## Scope and findings

The read-only audit covered all 18 published commits: 196 historical paths and 335 unique Git blobs, comprising 327 text files and eight screenshot versions. It also examined three GitHub Actions log archives, check outputs, repository settings and the available artifact/publication metadata.

No active credentials, private keys, customer data, unrelated project source, database files, runtime directories or model weights were found in that scope. The tracked `.env.example` contains only a comment. All 60 benchmark scenarios reconstruct from their synthetic generator and match their manifest hashes. The additional demonstration scenario is fictional.

All eight screenshot versions contain only the fictional workbench. Their PNG files have no EXIF/text metadata or appended content. Actions logs contain masked checkout credentials; no unmasked token was identified. GitHub secret scanning and push protection were enabled with zero alerts at the time of the audit.

## Metadata retained in history

The commit-author email matches the business email already published on the GitHub profile. It is public contact information, not a newly exposed private address.

Benchmark reports and the original implementation plan retain absolute author-workstation paths. These reveal a local username and directory layout, without exposing the contents of other directories. Hardware and runtime details establish measurement provenance.

Two obsolete local lease ownership tokens appear in the original model reports. They are random cleanup-ownership markers, not provider credentials. Both measured workers recorded completed cleanup; neither token matches the active machine lease or the project's running process records at audit time. No credential rotation is indicated by these findings.

Future public report exports omit absolute workstation paths and raw process-ownership tokens. Any derived export identifies its source report hash and redactions. Original frozen reports remain unchanged so their existing hashes and measured provenance stay verifiable.

## Limits

This is a bounded publication audit, not a guarantee that every possible secret format or application vulnerability has been detected. Dedicated Gitleaks/TruffleHog executables were unavailable. The audit combined credential-pattern, high-entropy and sensitive-assignment checks with source-context and image inspection.

Two dependency-cache entries were listed, but their payloads could not be inspected through the available API. Unreachable/deleted remote objects and third-party copies were outside scope. The audit did not change repository visibility or rewrite published Git history.

## Model-repair follow-up

A separate read-only review checked the initial model-repair changes and four curated five-case development reports. Each export's source hash and declared redactions matched its ignored raw report; results, scores and gates were unchanged. No credentials, private paths, ownership tokens, customer records, runtime files, weights or unrelated material were found in that reviewed snapshot. The public smoke manifest matches the input hash retained in those reports.

All 13 original evidence files remained byte-for-byte unchanged. The regression tests' invented private-owner path and `foreign` ownership marker are synthetic test inputs. The exporter removes specified provenance metadata; future report content still requires explicit inspection.

## Final Qwen v3 publication review

Follow-up dated 2026-10-16 covered all five unpublished commits after `d8956e0`: 156 new Git blobs across 133 paths, totaling 2,404,361 bytes, including intermediate file versions. All five commits use the verified GitHub noreply identity. The final working-tree audit covered 13 files and 482,985 bytes before the final review disclosures were appended. No credentials, private runtime paths, ownership tokens, weights, databases, customer data or unrelated material were detected in that scope. The path in the exporter regression is deliberately fictional.

Both final challenge exports match their raw reports after only the declared redactions, and their raw hashes verify. Results, scores, gates and case order remain unchanged. The actual model records 28/30 actions and outcomes, 22/24 completions and zero unapproved or duplicate effects; the fixture records 30/30 and 24/24. Both use clean source `a79256d`. Known false age claims are disclosed, unsupported-claim counts remain null and full factual acceptance remains open.

The fresh-archive report removes only its temporary root path and adds declared export/coordinator metadata. Raw-report and log hashes verify. All 11 commands exited successfully; the logs record 94 Python tests, eight component tests, three fixture browser passes and one explicitly skipped model test. All three regenerated contract files match the archived source. Actual inference and the native model browser run are separate evidence.

The v3 scenario bytes, manifests, checksums, provenance and runtime freeze were also checked against their retained source artifacts. Actual-model browser screenshots contain only the fictional workbench, with no EXIF/text metadata or trailing content. Browser attribution distinguishes coordinator checks from identifiers present in the raw capture. Frozen historical evidence remains unchanged.

The previously published-history audit and its limits still apply. This follow-up did not rewrite history or upload runtime artifacts. The [trace review](REVIEW-2026-10-16.md#frozen-v3-trace-review) records additional model explanation errors without changing measured reports or claiming completed human review.

## V4 repair publication review

Follow-up dated 2026-10-16 examined all nine unpublished commits after `791f08b`, comprising 96 new blobs and 2,321,210 bytes, including intermediate versions. The final evidence/documentation snapshot added 13 working files and 509,336 bytes before the trace-review and audit text was appended. All repair commits use the verified GitHub noreply identity. No credentials, private runtime paths, active ownership tokens, model weights, databases, customer records or unrelated source were found in that scope. The earlier published-history disclosures and bounded scanner limitations remain applicable.

Both final challenge exports exactly match their raw reports after only declared metadata redactions, and raw SHA-256 values verify. The model records 29/30 actions/outcomes and 23/24 completions; the fixture records 30/30 and 24/24. Both record zero unapproved or duplicate effects. The blocked timezone-uncertainty attempt has no proposal, approval, ticket or annotation. Diagnostics retain two incorrect intermediate fields and two unsupported reasons. Factual-review counts remain null; no zero-unsupported-claims claim is made.

All 104 frozen runtime/test/configuration hashes match the recorded checkpoints. All 51 original staging-inventory payloads verify. The 30 public scenarios, manifest and oracles match the frozen originals; all 33 public checksum entries pass. The public checksum file intentionally covers public paths and exports, rather than the larger private source/reference inventory. First access follows implementation freeze and actual-model browser verification. The separate authorship clarification identifies the case author as an AI agent and leaves original frozen wording unchanged.

The calibration and clean-archive exports preserve their measurements. All 11 archive logs verify: 137 Python tests, eight component tests, three fixture browser passes and one model skip. Separate actual-model browser evidence records four passes. Browser payload, probe, screenshots and hashes match their retained sources. Both PNGs contain only fictional application content and image chunks, without metadata or trailing content. Previously frozen evidence remains byte-identical.

A separate [30-case trace review](REVIEW-2026-10-16.md#frozen-v4-trace-review) records the model errors and examines all displayed explanations. Source review and model-assisted factual review do not establish completed human review, screen-reader accessibility or production acceptance. This publication pass does not rewrite prior Git history or upload ignored runtime artifacts.
