import asyncio
import json
import sqlite3
from datetime import timedelta
from pathlib import Path
from typing import Literal

import pytest

from casework_agent.clock import FrozenClock
from casework_agent.contracts import ApprovalRequest, CaseView, VersionRequest
from casework_agent.executor import Executor, Fenced
from casework_agent.hashing import canonical_json
from casework_agent.repository import Conflict, Repository
from casework_agent.worker import Worker
from tests.integration.test_approval import prepared
from tests.support import TestSystem


class SimulatedDeath(BaseException):
    pass


def request(case: CaseView, decision: Literal["approve", "reject"] = "approve") -> ApprovalRequest:
    assert case.proposal
    return ApprovalRequest(
        proposal_id=case.proposal.id,
        proposal_hash=case.proposal.hash,
        expected_case_version=case.version,
        decision=decision,
    )


async def bump(system: TestSystem, service: Literal["orders", "carrier"]) -> None:
    await system.stop_process(service)
    table = "orders" if service == "orders" else "shipments"
    with sqlite3.connect(system.root / f"{service}.sqlite3") as con:
        row = con.execute(f"SELECT id,payload FROM {table}").fetchone()
        payload = json.loads(row[1])
        payload["version"] += 1
        con.execute(f"UPDATE {table} SET payload=? WHERE id=?", (canonical_json(payload), row[0]))
    await system.spawn(service, f"mocks.{service}")


@pytest.mark.parametrize(
    "checkpoint",
    [
        "before_send",
        "ticket_committed_before_local_result",
        "annotation_committed_before_local_result",
    ],
)
async def test_worker_crash_boundaries(tmp_path: Path, checkpoint: str) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        await flow.decide(id, request(repo.get_case(id)), "approve")

        def crash(name: str) -> None:
            if name == checkpoint:
                raise SimulatedDeath(name)

        worker = Worker(repo, flow.settings, checkpoint=crash)
        with pytest.raises(SimulatedDeath):
            for _ in range(3):
                await worker.tick()
        path = repo.path
        future = repo.clock.now() + timedelta(seconds=31)
        repo.close()
        with Repository.open(path, FrozenClock(future)) as recovered:
            replacement = Worker(recovered, flow.settings)
            for _ in range(8):
                await replacement.tick()
            case = recovered.get_case(id)
            assert case.state == "completed"
            assert (await system.counts()).tickets == 1
            assert (await system.counts()).annotations == 1
            await replacement.close()


@pytest.mark.parametrize(
    "change", ["expiry", "policy", "order", "carrier", "version", "proposal_hash", "reject"]
)
async def test_approval_invalidations_and_rejection(tmp_path: Path, change: str) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            case = repo.get_case(id)
            assert case.proposal
            body = request(case)
            if change == "reject":
                result = await flow.decide(id, request(case, "reject"), "reject")
                assert result.state == "rejected" and not result.operations
                renewed = repo.command(
                    id, "repropose", VersionRequest(expected_case_version=result.version), "renew"
                )
                await flow.gather(renewed.id)
                proposal = repo.get_case(id).proposal
                assert proposal is not None and proposal.version == 2
            else:
                if change == "expiry":
                    repo.clock = FrozenClock(case.proposal.expires_at + timedelta(seconds=1))
                if change in {"order", "carrier"}:
                    await bump(system, "orders" if change == "order" else "carrier")
                if change == "version":
                    body.expected_case_version += 1
                if change == "proposal_hash":
                    body.proposal_hash = "0" * 64
                with pytest.raises(Conflict):
                    if change == "policy":
                        repo.apply_decision(id, body, "policy", 1, 1, "changed")
                    else:
                        await flow.decide(id, body, "approve")
                assert not repo.get_case(id).operations
            assert (await system.counts()).tickets == 0
            assert (await system.counts()).annotations == 0
        finally:
            repo.close()


async def test_partial_order_conflict_is_not_completed(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            await flow.decide(id, request(repo.get_case(id)), "approve")
            worker = Worker(repo, flow.settings)
            await worker.tick()
            assert repo.get_case(id).operations[0].state == "succeeded"
            await bump(system, "orders")
            await worker.tick()
            result = repo.get_case(id)
            assert result.state == "review_required"
            assert [o.state for o in result.operations] == ["succeeded", "rejected"]
            assert (await system.counts()).tickets == 1
            assert (await system.counts()).annotations == 0
            await worker.close()
        finally:
            repo.close()


async def test_carrier_change_after_approval_prevents_claim(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            await flow.decide(id, request(repo.get_case(id)), "approve")
            await bump(system, "carrier")
            worker = Worker(repo, flow.settings)
            await worker.tick()
            assert repo.get_case(id).state == "stale"
            assert not repo.get_case(id).operations
            assert (await system.counts()).tickets == 0
            await worker.close()
        finally:
            repo.close()


async def test_unknown_outage_explicit_reconcile_and_generation_fence(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            await flow.decide(id, request(repo.get_case(id)), "approve")
            worker = Worker(repo, flow.settings)
            assert worker.acquire()
            executor = Executor(repo, flow.settings, worker.owner, worker.generation)
            op = await executor.claim_next(id, worker.owner, worker.generation)
            assert op
            await system.stop_process("tickets")
            await executor.send(op)
            await executor.reconcile_operation(op)
            assert repo.get_case(id).state == "review_required"
            assert repo.get_case(id).operations[0].state == "unknown"
            case = repo.get_case(id)
            repo.command(
                id, "reconcile", VersionRequest(expected_case_version=case.version), "reconcile"
            )
            await system.spawn("tickets", "mocks.tickets")
            for _ in range(5):
                await worker.tick()
            assert repo.get_case(id).state == "completed"
            repo.clock = FrozenClock(repo.clock.now() + timedelta(seconds=31))
            other = Worker(repo, flow.settings)
            assert other.acquire()
            with pytest.raises(Fenced):
                executor.unknown(op, "late response")
            await other.close()
        finally:
            repo.close()


async def test_interrupted_gathering_requires_explicit_reproposal(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            case = await flow.decide(id, request(repo.get_case(id), "reject"), "reject")
            repo.command(
                id, "repropose", VersionRequest(expected_case_version=case.version), "renew"
            )
            assert repo.begin_gather(id)
            worker = Worker(repo, flow.settings)
            await worker.tick()
            case = repo.get_case(id)
            assert case.state == "failed" and case.error and case.error.code == "agent_interrupted"
            assert not case.operations
            await worker.close()
        finally:
            repo.close()


async def test_real_app_process_restart_preserves_pending_approval(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start(app=True)
        seed = {
            "scenario_id": "dev-delay-01",
            "order_id": "o-001",
            "as_of": "2026-10-15T12:00:00Z",
            "mode": "fixture",
        }
        created = await system.api.post(
            "/v1/cases", json=seed, headers={"Idempotency-Key": "create"}
        )
        case = await system.wait_state(created.json()["id"], "needs_approval")
        await system.stop_process("app")
        await system.spawn("app", "casework_agent.cli")
        restored = CaseView.model_validate((await system.api.get(f"/v1/cases/{case.id}")).json())
        assert restored.proposal == case.proposal
        assert restored.state == "needs_approval"
        assert (await system.counts()).tickets == 0
        await asyncio.sleep(0)


async def test_journal_hash_mismatch_and_exhausted_budget_remain_unknown(tmp_path: Path) -> None:
    from casework_agent.contracts import JournalResult

    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            await flow.decide(id, request(repo.get_case(id)), "approve")
            worker = Worker(repo, flow.settings)
            assert worker.acquire()
            executor = Executor(repo, flow.settings, worker.owner, worker.generation)
            op = await executor.claim_next(id, worker.owner, worker.generation)
            assert op and op.request_hash
            op.attempts = 3
            with repo.transaction():
                repo.save_operation(op)
            await executor.reconcile_operation(op)
            assert repo.get_case(id).operations[0].last_error == "send_budget_exhausted"
            await system.stop_process("tickets")
            fake = JournalResult(
                key=op.key,
                request_hash="0" * 64,
                outcome="succeeded",
                http_status=201,
                response_json={},
                committed_at=repo.clock.now(),
            )
            with sqlite3.connect(tmp_path / "tickets.sqlite3") as con:
                con.execute(
                    "INSERT INTO idempotency VALUES(?,?,?)",
                    (op.key, fake.request_hash, fake.model_dump_json()),
                )
            await system.spawn("tickets", "mocks.tickets")
            await executor.reconcile_operation(op)
            case = repo.get_case(id)
            assert case.state == "review_required"
            assert case.operations[0].last_error == "journal_hash_mismatch"
            assert case.operations[0].attempts == 3
            assert (await system.counts()).tickets == 0
            await worker.close()
        finally:
            repo.close()


async def test_cancel_during_scripted_model_gather_cannot_publish(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from casework_agent.config import Settings
    from casework_agent.contracts import CaseSeed
    from casework_agent.model_adapter import ChatMessage, ModelReply
    from casework_agent.workflow import Workflow

    entered, release = asyncio.Event(), asyncio.Event()

    class WaitingClient:
        async def complete(self, messages: list[ChatMessage]) -> ModelReply:
            entered.set()
            await release.wait()
            return ModelReply(text='{"kind":"tool","name":"create_ticket","arguments":{}}')

    with Repository.open(tmp_path / "app.sqlite3") as repo:
        case = repo.create_case(
            CaseSeed(
                scenario_id="cancel-test", order_id="o-001", as_of=datetime.now(UTC), mode="model"
            )
        )
        task = asyncio.create_task(
            Workflow(repo, Settings(root=tmp_path), WaitingClient()).gather(case.id)
        )
        await entered.wait()
        case = repo.get_case(case.id)
        repo.command(
            case.id, "cancel", VersionRequest(expected_case_version=case.version), "cancel"
        )
        release.set()
        await task
        final = repo.get_case(case.id)
        assert final.state == "cancelled" and final.proposal is None
        assert not final.operations and not final.evidence
