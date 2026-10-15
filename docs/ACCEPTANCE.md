# Acceptance record

Implementation date: 2026-10-15. This is a local single-operator simulation. No public release or production acceptance is claimed.

| Gate                                                    | Observed result                                                      |
| ------------------------------------------------------- | -------------------------------------------------------------------- |
| Fixture held-out actions                                | 30/30; passes the 27/30 target                                       |
| Fixture final outcomes                                  | 30/30; passes the 27/30 target                                       |
| Fixture authorised completions                          | 24/24; passes the 22/24 target                                       |
| Actual Qwen valid actions                               | 0/30; fails the 27/30 target                                         |
| Actual Qwen final outcomes                              | 0/30; fails the 27/30 target                                         |
| Actual Qwen authorised completions                      | 0/24; fails the 22/24 target                                         |
| Unapproved writes / duplicate effects                   | 0/0 in both defined evaluation runs                                  |
| Actual model claims review                              | Pending; unsupported_claims is null                                  |
| Real HTTP browser workflow                              | Passed with both post-commit response drops and exact request replay |
| Tested automated accessibility                          | Zero Axe findings in tested desktop/mobile and light/dark states     |
| Manual screen-reader testing                            | Not performed                                                        |
| Strict Python / TypeScript and test/build checks        | See current command/count evidence in STATE.md                       |
| Fresh whole-branch review / clean-checkout verification | See current status in STATE.md                                       |

The full [fixture](evidence/fixture-full.json) and [Qwen](evidence/qwen-full.json) reports retain every case and frozen manifest hash. Summary files link their source report hashes. The actual model report explicitly records 30 `invalid_model_output` failures. None reached valid approval; its zero-write count must not be interpreted as successful workflow completion.

The initial reports were measured on an in-progress dirty tree and identify the commit and dirty flag. Runtime version/snapshot provenance and exact assistant exchanges remain available. Later checked-in code is not automatically a remeasurement. STATE.md identifies any subsequent clean-checkpoint run.

Python fault checks use real HTTP services, owned database reopen checkpoints and a real application subprocess restart. They do not establish arbitrary distributed exactly-once execution. Browser checks include keyboard approval and reduced motion; automated checks cannot certify all assistive technology behavior.

No model, fixture or screenshot contains real customer data. All third-party model terms remain separate. Weights, bulk runtime files and credentials remain ignored. Source publication is authorized separately from deployment. See STATE.md for the current publication status; no deployment or external communications are implied.

Original implementation verification: clean checkpoint `1da911fb12bb896e750248a67f22345bf3d7892b` passed 53 Python tests, 5 component tests, all 3 browser flows and strict checks from a fresh archive. Latest evaluation reports record dirty=false; initial dirty-tree reports are retained separately. Model quality still fails; human claims and manual screen-reader reviews remain pending.
