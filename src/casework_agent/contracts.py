from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

type JsonDict = dict[str, JsonValue]
type Action = Literal["open_investigation", "manual_review"]
type Queue = Literal["delivery_investigation", "human_review"]
type Mode = Literal["fixture", "model"]
type CaseState = Literal["new", "gathering", "needs_approval", "approved", "executing", "completed", "failed", "rejected", "cancelled", "stale", "review_required"]
type OperationState = Literal["pending", "in_flight", "unknown", "succeeded", "rejected"]
type Identifier = Annotated[str, Field(min_length=1, max_length=160)]

def uid() -> str:
    return str(uuid4())

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

class CaseSeed(StrictModel):
    scenario_id: Identifier
    order_id: Identifier
    as_of: datetime
    mode: Mode = "fixture"
    @field_validator("as_of")
    @classmethod
    def utc_date(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Timezone required")
        return value.astimezone(UTC)

class OrderAnnotation(StrictModel):
    annotation_id: str = Field(default_factory=uid)
    ticket_id: str
    action: Action
    operation_key: str

class Order(StrictModel):
    order_id: Identifier
    shipment_id: Identifier
    status: Literal["in_transit", "delivered", "cancelled", "unknown"]
    version: int = Field(ge=1, default=1)
    note: str = Field(max_length=2000, default="")
    policy_exception: str | None = Field(default=None, max_length=500)
    annotations: list[OrderAnnotation] = Field(default_factory=lambda: list[OrderAnnotation]())

class CarrierEvent(StrictModel):
    code: str = Field(max_length=100)
    at: datetime
    description: str = Field(max_length=500)

class Shipment(StrictModel):
    shipment_id: Identifier
    status: Literal["delayed", "in_transit", "delivered", "unknown"]
    version: int = Field(ge=1, default=1)
    last_event_at: datetime | None
    conflicting_events: bool = False
    events: list[CarrierEvent] = Field(default_factory=lambda: list[CarrierEvent]())

class Policy(StrictModel):
    version: str
    hash: str
    delay_hours: int = 48
    approval_ttl_seconds: int = 900
    rules: list[str]

class Evidence(StrictModel):
    id: str = Field(default_factory=uid)
    case_id: str
    source: Literal["order", "carrier", "policy"]
    source_id: str
    source_version: str
    payload: Order | Shipment | Policy
    payload_hash: str
    fetched_at: datetime

class AgentDecision(StrictModel):
    action: Action
    rationale: str = Field(min_length=1, max_length=1000)
    draft_note: str = Field(min_length=1, max_length=500)
    evidence_ids: list[str] = Field(min_length=3, max_length=8)

class TicketIntent(StrictModel):
    kind: Literal["create_ticket"] = "create_ticket"
    order_id: str
    action: Action
    queue: Queue
    priority: Literal["normal"] = "normal"
    internal_note: str = Field(min_length=1, max_length=500)

class AnnotationIntent(StrictModel):
    kind: Literal["annotate_order"] = "annotate_order"
    order_id: str
    action: Action
    ticket_ref: Literal["$ticket"] = "$ticket"
    expected_order_version: int = Field(ge=1)

class Proposal(StrictModel):
    id: str = Field(default_factory=uid)
    case_id: str
    version: int
    policy_hash: str
    evidence_ids: list[str]
    evidence_hashes: list[str]
    order_version: int
    shipment_version: int
    action: Action
    rationale: str
    draft_note: str
    intents: tuple[TicketIntent, AnnotationIntent]
    created_at: datetime
    expires_at: datetime
    hash: str

class ApprovalRequest(StrictModel):
    proposal_id: str
    proposal_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_case_version: int = Field(ge=1)
    decision: Literal["approve", "reject"]

class VersionRequest(StrictModel):
    expected_case_version: int = Field(ge=1)

class Approval(StrictModel):
    id: str = Field(default_factory=uid)
    case_id: str
    proposal_id: str
    proposal_hash: str
    decision: Literal["approve", "reject"]
    actor: Literal["local_operator"] = "local_operator"
    created_at: datetime

class Operation(StrictModel):
    id: str = Field(default_factory=uid)
    case_id: str
    approval_id: str
    ordinal: Literal[1, 2]
    kind: Literal["create_ticket", "annotate_order"]
    key: str
    request_json: JsonDict | None = None
    request_hash: str | None = None
    state: OperationState = "pending"
    attempts: int = 0
    remote_id: str | None = None
    response_json: JsonDict | None = None
    last_error: str | None = None
    worker_generation: int = 0

class Ticket(StrictModel):
    ticket_id: str = Field(default_factory=uid)
    order_id: str
    action: Action
    queue: Queue
    priority: Literal["normal"]
    internal_note: str
    operation_key: str

class JournalResult(StrictModel):
    key: str
    request_hash: str
    outcome: Literal["succeeded", "rejected"]
    http_status: int
    response_json: JsonDict
    committed_at: datetime

class ApiError(StrictModel):
    code: str
    message: str
    retryable: bool = False
    case_id: str | None = None
    request_id: str = Field(default_factory=uid)
    details: JsonDict = Field(default_factory=dict)

class AuditEvent(StrictModel):
    id: int
    case_id: str
    kind: str
    payload: JsonDict
    created_at: datetime

class CaseView(StrictModel):
    id: str
    scenario_id: str
    order_id: str
    as_of: datetime
    mode: Mode
    state: CaseState
    version: int
    proposal: Proposal | None = None
    evidence: list[Evidence] = Field(default_factory=lambda: list[Evidence]())
    operations: list[Operation] = Field(default_factory=lambda: list[Operation]())
    events: list[AuditEvent] = Field(default_factory=lambda: list[AuditEvent]())
    available_actions: list[Literal["approve", "reject", "cancel", "repropose", "reconcile"]] = Field(default_factory=lambda: list[Literal["approve", "reject", "cancel", "repropose", "reconcile"]]())
    error: ApiError | None = None
