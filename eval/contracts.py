from typing import Literal

from pydantic import Field

from casework_agent.contracts import Action, CaseState, JsonDict, StrictModel


class ManifestRow(StrictModel):
    case_id: str
    family: str
    scenario_file: str
    scenario_hash: str
    as_of: str
    expected_action: Action
    expected_final_state: CaseState
    expected_ticket_count: int
    expected_annotation_count: int
    fault_checkpoint: str
    split: Literal["dev", "holdout"]


class Manifest(StrictModel):
    version: int
    authorship: str
    cases: list[ManifestRow]


class CaseResult(StrictModel):
    case_id: str
    family: str
    expected_action: Action
    proposed_action: Action | None
    expected_final_state: CaseState
    final_state: CaseState
    approved: bool
    unapproved_writes: int
    duplicate_effects: int
    unsupported_claims: int | None
    usage_tokens: int | None
    elapsed_ms: float
    tool_calls: int
    tickets: int
    annotations: int
    expected_tickets: int
    expected_annotations: int
    error: str | None = None
    proposal: JsonDict | None = None
    trace: JsonDict = Field(default_factory=dict)


class Score(StrictModel):
    total: int
    valid_action_count: int
    correct_workflow_count: int
    authorized_completion_count: int
    authorized_completion_denominator: int
    unapproved_writes: int
    duplicate_effects: int
    unsupported_claims: int | None
    claims_review_complete: bool
    unnecessary_escalations: int
    investigation_denominator: int
    usage_tokens: int | None
    latency_p50_ms: float | None
    latency_p95_ms: float | None
    failures: int
    families: dict[str, JsonDict]


class EvaluationReport(StrictModel):
    mode: Literal["fixture", "model"]
    provenance: JsonDict
    results: list[CaseResult]
    score: Score
    gates: JsonDict
