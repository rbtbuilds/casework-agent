import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from casework_agent.agent import AgentContext
from casework_agent.config import Settings
from casework_agent.contracts import AgentDecision, CaseSeed, Evidence, JsonDict, Order
from casework_agent.model_adapter import ChatMessage, LocalModelAdapter, ModelReply
from casework_agent.policy import allowed_action
from casework_agent.repository import Repository
from casework_agent.tools import ReadTools
from casework_agent.worker import Worker
from tests.support import TestSystem


class ScriptedReadClient:
    """Protocol-only test client. This is not model inference evidence."""

    async def complete(
        self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
    ) -> ModelReply:
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
                "assessment": {
                    "order_in_transit": True,
                    "shipment_delayed": True,
                    "no_policy_exception": True,
                    "no_conflicting_or_terminal_events": True,
                    "timestamps_known_and_consistent": True,
                    "age_at_least_48_hours": True,
                },
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
            assert len(adapter.trace) == 10
            assert adapter.usage_tokens is None
            assert (await system.counts()).tickets == 0
        finally:
            await tools.close()


@pytest.mark.parametrize("timestamp", ["0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00"])
async def test_unrepresentable_utc_clock_does_not_stop_following_case(
    tmp_path: Path, timestamp: str
) -> None:
    source = Path(__file__).resolve().parents[2] / "fixtures/scenarios/dev-delay-01.json"
    scenario = json.loads(source.read_text())
    scenario["shipment"]["events"] = [
        {"code": "scan", "at": timestamp, "description": "Fictional date boundary."}
    ]
    (tmp_path / "scenario.json").write_text(json.dumps(scenario))
    async with TestSystem(tmp_path) as system:
        await system.start()
        with Repository.open(tmp_path / ".runtime/app.sqlite3") as repo:
            worker = Worker(repo, Settings(root=tmp_path), model=ScriptedReadClient())
            try:
                invalid = repo.create_case(
                    CaseSeed(
                        scenario_id="boundary",
                        order_id="o-001",
                        mode="model",
                        as_of=datetime(2026, 10, 15, 12, tzinfo=UTC),
                    )
                )
                assert await worker.tick()
                failed = repo.get_case(invalid.id)
                assert failed.state == "failed"
                assert failed.error and failed.error.code == "timestamp_out_of_utc_range"
                assert failed.proposal is None and not failed.operations
                following = repo.create_case(
                    CaseSeed(
                        scenario_id="following",
                        order_id="o-001",
                        mode="fixture",
                        as_of=datetime(2026, 10, 15, 12, tzinfo=UTC),
                    )
                )
                assert await worker.tick()
                assert repo.get_case(following.id).state == "needs_approval"
                counts = await system.counts()
                assert counts.tickets == 0 and counts.annotations == 0
            finally:
                await worker.close()
