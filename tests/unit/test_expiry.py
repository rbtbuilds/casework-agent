from datetime import timedelta
from pathlib import Path

from casework_agent.clock import FrozenClock
from casework_agent.contracts import VersionRequest
from tests.integration.test_approval import prepared
from tests.support import TestSystem


async def test_expiry_exposes_reproposal_without_cancellation(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        try:
            case = repo.get_case(id)
            assert case.proposal
            repo.clock = FrozenClock(case.proposal.expires_at + timedelta(seconds=1))
            repo.expire_unclaimed()
            expired = repo.get_case(id)
            assert expired.state == "stale" and expired.available_actions == ["repropose"]
            repo.command(
                id, "repropose", VersionRequest(expected_case_version=expired.version), "renew"
            )
            await flow.gather(id)
            renewed = repo.get_case(id)
            assert renewed.proposal and renewed.proposal.version == 2
            assert renewed.state == "needs_approval" and "approve" in renewed.available_actions
            assert (await system.counts()).tickets == 0
        finally:
            repo.close()
