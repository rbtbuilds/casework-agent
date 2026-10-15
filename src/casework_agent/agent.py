from datetime import datetime
from typing import Protocol

from .contracts import AgentDecision, StrictModel
from .policy import allowed_action
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
    if decision.action != allowed_action(tools.order, tools.shipment, context.as_of):
        raise AgentValidationError("policy_mismatch")
