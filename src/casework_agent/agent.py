from datetime import datetime
from typing import Protocol

from .contracts import AgentDecision, StrictModel
from .hashing import canonical_hash
from .policy import allowed_action, current_policy
from .tools import ReadTools


class AgentContext(StrictModel):
    case_id: str
    order_id: str
    as_of: datetime


class AgentAdapter(Protocol):
    async def propose(self, context: AgentContext, tools: ReadTools) -> AgentDecision: ...


class AgentValidationError(ValueError):
    pass


class FixtureAdapter:
    async def propose(self, context: AgentContext, tools: ReadTools) -> AgentDecision:
        await tools.get_order(context.order_id)
        assert tools.order is not None
        await tools.get_shipment(tools.order.shipment_id)
        await tools.get_policy()
        assert tools.shipment is not None
        action = allowed_action(tools.order, tools.shipment, context.as_of)
        return AgentDecision(
            action=action,
            rationale="Fixed fictional policy applied to the observed order,carrier and policy evidence.",
            draft_note="Fictional internal case: review the recorded carrier delay; no customer contact or compensation is authorised.",
            evidence_ids=[e.id for e in tools.evidence],
        )


def validate_decision(context: AgentContext, tools: ReadTools, decision: AgentDecision) -> None:
    if (
        tools.case_id != context.case_id
        or tools.order_id != context.order_id
        or (tools.order is not None and tools.order.order_id != context.order_id)
        or (
            tools.order is not None
            and tools.shipment is not None
            and tools.shipment.shipment_id != tools.order.shipment_id
        )
    ):
        raise AgentValidationError("evidence_scope")
    ids = set(decision.evidence_ids)
    matching = [e for e in tools.evidence if e.id in ids]
    if (
        len(ids) != len(decision.evidence_ids)
        or len(matching) != len(ids)
        or {e.source for e in matching} != {"order", "carrier", "policy"}
    ):
        raise AgentValidationError("evidence_coverage")
    if tools.order is None or tools.shipment is None:
        raise AgentValidationError("missing_evidence")
    latest = {
        "order": canonical_hash(tools.order.model_dump(mode="json")),
        "carrier": canonical_hash(tools.shipment.model_dump(mode="json")),
        "policy": canonical_hash(current_policy().model_dump(mode="json")),
    }
    if any(
        e.case_id != context.case_id
        or e.payload_hash != latest[e.source]
        or canonical_hash(e.payload.model_dump(mode="json")) != e.payload_hash
        for e in matching
    ):
        raise AgentValidationError("evidence_revision")
    if decision.action != allowed_action(tools.order, tools.shipment, context.as_of):
        raise AgentValidationError("policy_mismatch")
