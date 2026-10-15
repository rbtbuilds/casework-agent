from .contracts import CaseView, VersionRequest, uid
from .repository import Repository
from .worker import Worker


class Recovery:
    def __init__(self, repo: Repository, worker: Worker) -> None:
        self.repo, self.worker = repo, worker

    async def reconcile(self, case_id: str) -> CaseView:
        case = self.repo.get_case(case_id)
        self.repo.command(
            case_id, "reconcile", VersionRequest(expected_case_version=case.version), uid()
        )
        await self.worker.tick()
        return self.repo.get_case(case_id)
