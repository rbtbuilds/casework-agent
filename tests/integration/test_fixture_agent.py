from datetime import UTC, datetime
from pathlib import Path

import pytest

from casework_agent.agent import AgentContext, FixtureAdapter
from casework_agent.config import Settings
from casework_agent.tools import ReadTools, ToolPermissionError
from tests.support import TestSystem


async def test_scope_and_fixture_use_actual_services(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        tools = ReadTools("case-1", "o-001", Settings(root=tmp_path))
        with pytest.raises(ToolPermissionError):
            await tools.get_order("other-order")
        assert tools.request_count == 0
        with pytest.raises(ToolPermissionError):
            await tools.get_shipment("s-001")
        context = AgentContext(
            case_id="case-1", order_id="o-001", as_of=datetime(2026, 10, 15, 12, tzinfo=UTC)
        )
        decision = await FixtureAdapter().propose(context, tools)
        assert decision.action == "open_investigation"
        assert len(decision.evidence_ids) == 3
        assert {e.source for e in tools.evidence} == {"order", "carrier", "policy"}
        assert (await system.counts()).tickets == 0
        await tools.close()
