from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, cast

from jsonschema import Draft202012Validator

from casework_agent.agent import AgentContext
from casework_agent.config import Settings
from casework_agent.contracts import AgentDecision, JsonDict, Order, Shipment
from casework_agent.policy import current_policy
from casework_agent.tools import ReadTools


class Validator(Protocol):
    def is_valid(self, instance: object) -> bool: ...


def validator(schema: JsonDict) -> Validator:
    return cast(Validator, Draft202012Validator(schema))


async def test_generation_restricts_reads_to_known_case_ids_before_proposals(
    tmp_path: Path,
) -> None:
    from casework_agent.model_adapter import generation_schema

    tools = ReadTools("case", "order", Settings(root=tmp_path))
    context = AgentContext(case_id="case", order_id="order", as_of=datetime.now(UTC))
    try:
        initial = validator(generation_schema(context, tools))
        assert initial.is_valid(
            {"kind": "tool", "name": "get_order", "arguments": {"order_id": "order"}}
        )
        assert not initial.is_valid(
            {"kind": "tool", "name": "get_order", "arguments": {"order_id": "foreign"}}
        )
        assert not initial.is_valid({"kind": "tool", "name": "get_order"})
        assert not initial.is_valid({"kind": "proposal", "decision": {}})
        tools.order = Order(order_id="order", shipment_id="shipment", status="in_transit")
        tools.record("order", "order", "1", tools.order)
        after_order = validator(generation_schema(context, tools))
        assert after_order.is_valid(
            {"kind": "tool", "name": "get_shipment", "arguments": {"shipment_id": "shipment"}}
        )
        assert not after_order.is_valid(
            {"kind": "tool", "name": "get_shipment", "arguments": {"shipment_id": "foreign"}}
        )
        assert not after_order.is_valid({"kind": "tool", "name": "create_ticket", "arguments": {}})
    finally:
        await tools.close()


async def test_final_schema_keeps_the_action_model_chosen_but_binds_citations(
    tmp_path: Path,
) -> None:
    from casework_agent.model_adapter import generation_schema

    tools = ReadTools("case", "order", Settings(root=tmp_path))
    context = AgentContext(case_id="case", order_id="order", as_of=datetime.now(UTC))
    try:
        tools.order = Order(order_id="order", shipment_id="shipment", status="in_transit")
        tools.shipment = Shipment(
            shipment_id="shipment", status="delayed", last_event_at=context.as_of
        )
        tools.record("order", "order", "1", tools.order)
        tools.record("carrier", "shipment", "1", tools.shipment)
        policy = current_policy()
        tools.record("policy", policy.version, policy.hash, policy)
        schema = validator(generation_schema(context, tools))
        for action in ["open_investigation", "manual_review"]:
            decision: JsonDict = {
                "action": action,
                "rationale": "Recorded evidence.",
                "draft_note": "Fictional internal note.",
                "evidence_ids": [e.id for e in tools.evidence],
            }
            assert schema.is_valid({"kind": "proposal", "decision": decision})
            assert not schema.is_valid(
                {"kind": "proposal", "decision": {**decision, "evidence_ids": ["invented"] * 3}}
            )
            assert not schema.is_valid(
                {"kind": "proposal", "decision": {**decision, "action": "refund"}}
            )
            AgentDecision.model_validate(decision)
        assert not schema.is_valid({"kind": "tool", "name": "get_policy", "arguments": {}})
    finally:
        await tools.close()


async def test_model_facts_use_business_clock_and_raw_status_without_policy_answer(
    tmp_path: Path,
) -> None:
    from casework_agent.model_adapter import decision_facts

    tools = ReadTools("case", "order", Settings(root=tmp_path))
    context = AgentContext(
        case_id="case", order_id="order", as_of=datetime.fromisoformat("2026-10-15T12:00:00+00:00")
    )
    tools.order = Order(order_id="order", shipment_id="shipment", status="in_transit")
    tools.shipment = Shipment(
        shipment_id="shipment",
        status="in_transit",
        last_event_at=datetime.fromisoformat("2026-10-13T02:00:00+02:00"),
    )
    try:
        facts = decision_facts(context, tools)
        assert facts["elapsed_hours_since_last_event"] == 60.0
        assert facts["shipment_status"] == "in_transit"
        assert facts["order_status"] == "in_transit"
        assert not {"action", "expected_action", "allowed_action", "eligible"} & facts.keys()
        tools.shipment.last_event_at = None
        assert decision_facts(context, tools)["elapsed_hours_since_last_event"] is None
        tools.shipment.last_event_at = datetime(2026, 10, 13)
        assert decision_facts(context, tools)["elapsed_hours_since_last_event"] is None
    finally:
        await tools.close()
