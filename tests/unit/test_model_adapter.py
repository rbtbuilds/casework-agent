import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from casework_agent.agent import AgentContext, AgentValidationError
from casework_agent.config import Settings
from casework_agent.contracts import JsonDict
from casework_agent.model_adapter import ChatMessage, LocalModelAdapter, ModelReply
from casework_agent.model_session import MachineLease, ModelBusy
from casework_agent.tools import ReadTools


class MaliciousClient:
    async def complete(
        self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
    ) -> ModelReply:
        return ModelReply(text='{"kind":"tool","name":"create_ticket","arguments":{}}')


async def test_model_cannot_dispatch_writes(tmp_path: Path) -> None:
    tools = ReadTools("case-1", "o-001", Settings(root=tmp_path))
    try:
        with pytest.raises(AgentValidationError):
            await LocalModelAdapter(MaliciousClient()).propose(
                AgentContext(case_id="case-1", order_id="o-001", as_of=datetime.now(UTC)), tools
            )
        assert tools.request_count == 0
    finally:
        await tools.close()


def test_machine_lease_does_not_steal_another_owner(tmp_path: Path) -> None:
    lock = tmp_path / "ml.lock"
    lease = MachineLease(lock)
    lease.acquire("test")
    try:
        with pytest.raises(ModelBusy):
            MachineLease(lock).acquire("other")
        assert lock.is_dir()
    finally:
        lease.release()
    assert not lock.exists()


async def test_model_deadline_includes_awaited_tools(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import asyncio

    import casework_agent.model_adapter as module

    class ReadClient:
        async def complete(
            self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
        ) -> ModelReply:
            return ModelReply(
                text='{"kind":"tool","name":"get_order","arguments":{"order_id":"o"}}'
            )

    async def stalled_order(_order_id: str) -> None:
        await asyncio.sleep(5)

    tools = ReadTools("c", "o", Settings(root=tmp_path))
    monkeypatch.setattr(tools, "get_order", stalled_order)
    monkeypatch.setattr(module, "CASE_DEADLINE_SECONDS", 0.02, raising=False)
    try:
        async with asyncio.timeout(0.2):
            with pytest.raises(AgentValidationError, match="model_deadline"):
                await LocalModelAdapter(ReadClient()).propose(
                    AgentContext(case_id="c", order_id="o", as_of=datetime.now(UTC)), tools
                )
    finally:
        await tools.close()


async def test_wrong_policy_action_fails_without_feedback_or_second_guess(tmp_path: Path) -> None:
    from datetime import timedelta

    from casework_agent.contracts import AgentDecision, Order, Shipment
    from casework_agent.policy import current_policy

    tools = ReadTools("case", "order", Settings(root=tmp_path))
    context = AgentContext(case_id="case", order_id="order", as_of=datetime.now(UTC))
    tools.order = Order(order_id="order", shipment_id="shipment", status="in_transit")
    tools.shipment = Shipment(
        shipment_id="shipment", status="delayed", last_event_at=context.as_of - timedelta(hours=60)
    )
    tools.record("order", "order", "1", tools.order)
    tools.record("carrier", "shipment", "1", tools.shipment)
    policy = current_policy()
    tools.record("policy", policy.version, policy.hash, policy)

    class WrongAction:
        calls = 0

        async def complete(
            self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
        ) -> ModelReply:
            self.calls += 1
            decision = AgentDecision(
                action="manual_review",
                rationale="Incorrect policy choice.",
                draft_note="Fictional internal case: review.",
                evidence_ids=[e.id for e in tools.evidence],
            )
            return ModelReply(
                text=json.dumps(
                    {
                        "kind": "proposal",
                        "assessment": {
                            "order_in_transit": True,
                            "shipment_delayed": True,
                            "no_policy_exception": True,
                            "no_conflicting_or_terminal_events": True,
                            "timestamps_known_and_consistent": True,
                            "age_at_least_48_hours": True,
                        },
                        "primary_reason": "all_pass",
                        "decision": {
                            "action": decision.action,
                            "evidence_ids": decision.evidence_ids,
                        },
                    }
                )
            )

    client = WrongAction()
    try:
        with pytest.raises(AgentValidationError, match="policy_mismatch"):
            await LocalModelAdapter(client).propose(context, tools)
        assert client.calls == 1
    finally:
        await tools.close()
