import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from casework_agent.clock import FrozenClock
from casework_agent.config import Settings
from casework_agent.contracts import AgentDecision, CaseSeed, Order, Shipment, VersionRequest
from casework_agent.policy import current_policy
from casework_agent.repository import Repository
from casework_agent.tools import ReadTools
from casework_agent.worker import Worker


async def test_superseded_gather_cannot_publish_fail_or_save_trace(tmp_path: Path) -> None:
    clock = FrozenClock(datetime(2026, 10, 15, 12, tzinfo=UTC))
    root = Path(__file__).resolve().parents[2]
    raw = json.loads((root / "fixtures/scenarios/dev-delay-01.json").read_text())
    tools = ReadTools("case", "o-001", Settings(root=tmp_path))
    try:
        with Repository.open(tmp_path / "app.sqlite3", clock) as repo:
            case = repo.create_case(
                CaseSeed(scenario_id="dev-delay-01", order_id="o-001", as_of=clock.now())
            )
            tools.case_id = case.id
            tools.order, tools.shipment = (
                Order.model_validate(raw["order"]),
                Shipment.model_validate(raw["shipment"]),
            )
            tools.record("order", "o-001", "1", tools.order)
            tools.record("carrier", "s-001", "1", tools.shipment)
            policy = current_policy()
            tools.record("policy", policy.version, policy.hash, policy)
            decision = AgentDecision(
                action="open_investigation",
                rationale="Fictional recorded delay.",
                draft_note="Fictional note.",
                evidence_ids=[e.id for e in tools.evidence],
            )
            first = Worker(repo, Settings(root=tmp_path))
            assert first.acquire()
            old = repo.begin_gather(case.id, first.owner, first.generation)
            assert old
            clock.value += timedelta(seconds=31)
            replacement = Worker(repo, Settings(root=tmp_path))
            assert replacement.acquire()
            failed = repo.get_case(case.id)
            assert failed.state == "failed"
            repo.command(
                case.id, "repropose", VersionRequest(expected_case_version=failed.version), "renew"
            )
            new = repo.begin_gather(case.id, replacement.owner, replacement.generation)
            assert new
            repo.publish(case.id, decision, tools, {"status": "old"}, old)
            repo.fail_gather(case.id, "late_failure", old, {"status": "old"})
            current = repo.get_case(case.id)
            assert (
                current.state == "gathering" and current.proposal is None and current.error is None
            )
            assert repo.con.execute("SELECT COUNT(*) FROM agent_runs").fetchone()[0] == 0
            decision.evidence_ids.reverse()
            repo.publish(case.id, decision, tools, {"status": "new"}, new)
            assert repo.get_case(case.id).state == "needs_approval"
            assert repo.con.execute("SELECT COUNT(*) FROM agent_runs").fetchone()[0] == 1
            current = repo.get_case(case.id)
            assert current.proposal
            evidence = {e.id: e for e in current.evidence}
            assert current.proposal.evidence_hashes == [
                evidence[eid].payload_hash for eid in current.proposal.evidence_ids
            ]
            from casework_agent.contracts import ApprovalRequest

            rejected = repo.apply_decision(
                case.id,
                ApprovalRequest(
                    proposal_id=current.proposal.id,
                    proposal_hash=current.proposal.hash,
                    expected_case_version=current.version,
                    decision="reject",
                ),
                "reject",
                1,
                1,
                current.proposal.policy_hash,
            )
            repo.command(
                case.id,
                "repropose",
                VersionRequest(expected_case_version=rejected.version),
                "again",
            )
            assert repo.begin_gather(case.id, replacement.owner, replacement.generation)
            clock.value += timedelta(seconds=31)
            assert first.acquire()
            assert repo.get_case(case.id).state == "failed"
            await first.close()
            await replacement.close()
    finally:
        await tools.close()
