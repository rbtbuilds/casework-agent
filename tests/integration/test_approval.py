from datetime import UTC, datetime
from pathlib import Path

import pytest

from casework_agent.config import Settings
from casework_agent.contracts import ApprovalRequest, CaseSeed
from casework_agent.repository import Conflict, Repository
from casework_agent.workflow import Workflow
from tests.support import TestSystem


async def prepared(root: Path) -> tuple[Repository,Workflow,str]:
    repo=Repository.open(root/".runtime/app.sqlite3")
    flow=Workflow(repo,Settings(root=root,run_worker=False))
    case=repo.create_case(CaseSeed(scenario_id="dev-delay-01",order_id="o-001",as_of=datetime(2026,10,15,12,tzinfo=UTC),mode="fixture"))
    await flow.gather(case.id)
    return repo,flow,case.id

async def test_exact_approval_replay_and_changed_hash(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo,flow,id=await prepared(tmp_path)
        try:
            case=repo.get_case(id)
            assert case.proposal is not None and case.state=="needs_approval"
            wrong=ApprovalRequest(proposal_id=case.proposal.id,proposal_hash="0"*64,expected_case_version=case.version,decision="approve")
            with pytest.raises(Conflict):await flow.decide(id,wrong,"bad-hash")
            assert not repo.get_case(id).operations
            request=wrong.model_copy(update={"proposal_hash":case.proposal.hash})
            first=await flow.decide(id,request,"approve-once")
            replay=await flow.decide(id,request,"approve-once")
            assert first==replay and first.state=="approved"
            assert len(first.operations)==2
            assert all(o.attempts==0 for o in first.operations)
            assert (await system.counts()).tickets==0
            with pytest.raises(Conflict):await flow.decide(id,wrong,"approve-once")
        finally:repo.close()

async def test_stale_evidence_cannot_create_operations(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo,_flow,id=await prepared(tmp_path)
        try:
            case=repo.get_case(id)
            assert case.proposal is not None
            proposal=case.proposal
            request=ApprovalRequest(proposal_id=proposal.id,proposal_hash=proposal.hash,expected_case_version=case.version,decision="approve")
            with pytest.raises(Conflict):
                repo.apply_decision(id,request,"stale",99,1,proposal.policy_hash)
            assert repo.get_case(id).state=="stale"
            assert not repo.get_case(id).operations
        finally:repo.close()
