import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from casework_agent.agent import AgentContext, AgentValidationError, validate_decision
from casework_agent.config import Settings
from casework_agent.contracts import AgentDecision, Order, Shipment
from casework_agent.policy import current_policy
from casework_agent.tools import ReadTools


async def test_cited_source_must_match_bound_latest_revision() -> None:
    root = Path(__file__).resolve().parents[2]
    seed = json.loads((root / "fixtures/scenarios/dev-delay-01.json").read_text())
    order, shipment = Order.model_validate(seed["order"]), Shipment.model_validate(seed["shipment"])
    tools = ReadTools("case", "o-001", Settings(root=root))
    try:
        old = tools.record("order", order.order_id, "1", order)
        carrier = tools.record("carrier", shipment.shipment_id, "1", shipment)
        policy = current_policy()
        rules = tools.record("policy", policy.version, policy.hash, policy)
        tools.order = order.model_copy(update={"version": 2})
        tools.shipment = shipment
        tools.record("order", order.order_id, "2", tools.order)
        decision = AgentDecision(
            action="open_investigation",
            rationale="Fictional delay policy.",
            draft_note="Fictional note.",
            evidence_ids=[old.id, carrier.id, rules.id],
        )
        with pytest.raises(AgentValidationError, match="evidence_revision"):
            validate_decision(
                AgentContext(
                    case_id="case", order_id="o-001", as_of=datetime(2026, 10, 15, 12, tzinfo=UTC)
                ),
                tools,
                decision,
            )
    finally:
        await tools.close()
