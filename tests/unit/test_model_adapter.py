from datetime import UTC, datetime
from pathlib import Path

import pytest

from casework_agent.agent import AgentContext, AgentValidationError
from casework_agent.config import Settings
from casework_agent.model_adapter import ChatMessage, LocalModelAdapter, ModelReply
from casework_agent.model_session import MachineLease, ModelBusy
from casework_agent.tools import ReadTools


class MaliciousClient:
    async def complete(self, messages: list[ChatMessage]) -> ModelReply:
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
