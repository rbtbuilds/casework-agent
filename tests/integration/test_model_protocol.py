import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from casework_agent.agent import AgentContext
from casework_agent.config import Settings
from casework_agent.contracts import AgentDecision, Evidence, JsonDict, Order
from casework_agent.model_adapter import ChatMessage, LocalModelAdapter, ModelReply
from casework_agent.policy import allowed_action
from casework_agent.tools import ReadTools
from tests.support import TestSystem


class ScriptedReadClient:
    """Protocol-only test client. This is not model inference evidence."""

    async def complete(self, messages: list[ChatMessage]) -> ModelReply:
        observations = [
            Evidence.model_validate_json(m.content.removeprefix("UNTRUSTED_OBSERVATION="))
            for m in messages
            if m.content.startswith("UNTRUSTED_OBSERVATION=")
        ]
        if not observations:
            body: JsonDict = {
                "kind": "tool",
                "name": "get_order",
                "arguments": {"order_id": "o-001"},
            }
        elif len(observations) == 1:
            order = observations[0].payload
            assert isinstance(order, Order)
            body = {
                "kind": "tool",
                "name": "get_shipment",
                "arguments": {"shipment_id": order.shipment_id},
            }
        elif len(observations) == 2:
            body = {"kind": "tool", "name": "get_policy", "arguments": {}}
        else:
            decision = AgentDecision(
                action="open_investigation",
                rationale="Recorded delay meets the fictional policy.",
                draft_note="Fictional trace request.",
                evidence_ids=[e.id for e in observations],
            )
            body = {
                "kind": "proposal",
                "decision": cast(JsonDict, decision.model_dump(mode="json")),
            }
        return ModelReply(text=json.dumps(body))


async def test_scripted_json_loop_uses_real_read_http_only(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        tools = ReadTools("case", "o-001", Settings(root=tmp_path))
        try:
            context = AgentContext(
                case_id="case", order_id="o-001", as_of=datetime(2026, 10, 15, 12, tzinfo=UTC)
            )
            adapter = LocalModelAdapter(ScriptedReadClient())
            decision = await adapter.propose(context, tools)
            assert tools.order and tools.shipment
            assert decision.action == allowed_action(tools.order, tools.shipment, context.as_of)
            assert tools.request_count == 2 and tools.calls == 3
            assert len(adapter.trace) == 9
            assert adapter.usage_tokens is None
            assert (await system.counts()).tickets == 0
        finally:
            await tools.close()
