from pathlib import Path

import pytest

from casework_agent.contracts import ApprovalRequest, VersionRequest
from casework_agent.repository import Conflict
from casework_agent.worker import Worker
from tests.integration.test_approval import prepared
from tests.support import TestSystem


async def test_drop_after_ticket_commit_recovers_once(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start(ticket_drop_after_commit=True)
        repo, flow, id = await prepared(tmp_path)
        try:
            case = repo.get_case(id)
            assert case.proposal
            await flow.decide(id, ApprovalRequest(proposal_id=case.proposal.id, proposal_hash=case.proposal.hash, expected_case_version=case.version, decision="approve"), "approve")
            worker = Worker(repo, flow.settings)
            for _ in range(8):
                await worker.tick()
            result = repo.get_case(id)
            assert result.state == "completed"
            assert [o.state for o in result.operations] == ["succeeded", "succeeded"]
            assert (await system.counts()).tickets == 1
            assert (await system.counts()).annotations == 1
            with pytest.raises(Conflict, match="execution_started"):
                repo.command(id, "cancel", VersionRequest(expected_case_version=result.version), "cancel")
            await worker.close()
        finally:
            repo.close()


async def test_cancel_wins_before_claim_and_second_worker_is_fenced(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            case = repo.get_case(id)
            assert case.proposal
            approved = await flow.decide(id, ApprovalRequest(proposal_id=case.proposal.id, proposal_hash=case.proposal.hash, expected_case_version=case.version, decision="approve"), "approve")
            repo.command(id, "cancel", VersionRequest(expected_case_version=approved.version), "cancel")
            first, second = Worker(repo, flow.settings), Worker(repo, flow.settings)
            await first.tick()
            assert not await second.tick()
            assert repo.get_case(id).state == "cancelled"
            assert (await system.counts()).tickets == 0
            await first.close()
            await second.close()
        finally:
            repo.close()
