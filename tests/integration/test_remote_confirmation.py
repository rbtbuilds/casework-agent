from pathlib import Path

import httpx
import pytest

from casework_agent import executor as module
from casework_agent.contracts import JsonDict
from casework_agent.executor import Executor
from casework_agent.worker import Worker
from tests.e2e.test_failure_matrix import request
from tests.integration.test_approval import prepared
from tests.support import TestSystem


@pytest.mark.parametrize("ordinal", [1, 2])
@pytest.mark.parametrize("invalid_id", [None, ""])
async def test_malformed_write_confirmation_recovers_from_the_real_journal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ordinal: int, invalid_id: str | None
) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        repo, flow, id = await prepared(tmp_path)
        worker = Worker(repo, flow.settings)
        try:
            await flow.decide(id, request(repo.get_case(id)), "approve")
            if ordinal == 2:
                await worker.tick()
            assert worker.acquire()
            executor = Executor(repo, flow.settings, worker.owner, worker.generation)
            op = await executor.claim_next(id, worker.owner, worker.generation)
            assert op and op.ordinal == ordinal
            original = module.bounded_request

            async def malformed(
                client: httpx.AsyncClient,
                method: str,
                url: str,
                *,
                deadline: float,
                body: JsonDict | None = None,
                headers: dict[str, str] | None = None,
            ) -> httpx.Response:
                response = await original(
                    client, method, url, deadline=deadline, body=body, headers=headers
                )
                data = response.json()
                field = "ticket_id" if ordinal == 1 else "annotation_id"
                if invalid_id is None:
                    del data[field]
                else:
                    data[field] = invalid_id
                return httpx.Response(response.status_code, json=data, request=response.request)

            with monkeypatch.context() as patch:
                patch.setattr(module, "bounded_request", malformed)
                await executor.send(op)
            unknown = repo.get_case(id)
            assert unknown.state == "review_required"
            saved = unknown.operations[ordinal - 1]
            assert saved.state == "unknown" and saved.remote_id is None
            await executor.reconcile_operation(saved)
            for _ in range(3):
                await worker.tick()
            assert repo.get_case(id).state == "completed"
            assert (await system.counts()).tickets == 1
            assert (await system.counts()).annotations == 1
        finally:
            await worker.close()
            repo.close()
