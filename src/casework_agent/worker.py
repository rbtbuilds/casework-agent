import os
from collections.abc import Callable
from datetime import datetime, timedelta

from .config import Settings
from .contracts import ApiError, uid
from .executor import Executor, Fenced
from .model_adapter import ModelClient
from .repository import Repository
from .tools import DependencyError
from .workflow import Workflow


class Worker:
    def __init__(
        self,
        repo: Repository,
        settings: Settings,
        checkpoint: Callable[[str], None] | None = None,
        model: ModelClient | None = None,
    ) -> None:
        self.repo, self.settings = repo, settings
        self.owner, self.generation = uid(), 0
        self.started = False
        self.checkpoint, self.model = checkpoint, model

    def acquire(self) -> bool:
        now = self.repo.clock.now()
        with self.repo.transaction():
            row = self.repo.con.execute("SELECT * FROM worker_lease WHERE singleton=1").fetchone()
            if (
                row
                and row["owner_id"] != self.owner
                and datetime.fromisoformat(row["heartbeat_at"]) > now - timedelta(seconds=30)
            ):
                return False
            generation = int(row["generation"]) if row else 0
            if not row or row["owner_id"] != self.owner:
                generation += 1
            self.generation = generation
            self.repo.con.execute(
                "INSERT OR REPLACE INTO worker_lease VALUES(1,?,?,?,?,?)",
                (self.owner, os.getpid(), generation, now.isoformat(), now.isoformat()),
            )
            if not self.started:
                for case in self.repo.list_cases():
                    if case.state == "gathering":
                        self.repo.transition(
                            case.id,
                            "failed",
                            "agent_interrupted",
                            ApiError(
                                code="agent_interrupted",
                                message="Interrupted proposal; explicitly repropose.",
                                case_id=case.id,
                            ),
                        )
                    for op in case.operations:
                        if op.state == "in_flight":
                            op.state = "unknown"
                            self.repo.save_operation(op)
                            self.repo.transition(
                                case.id, "review_required", "interrupted_operation"
                            )
                    if any(o.state in {"unknown", "in_flight"} for o in case.operations):
                        self.repo.con.execute(
                            "UPDATE cases SET reconcile_requested=1 WHERE id=?", (case.id,)
                        )
                self.started = True
        return True

    def heartbeat(self) -> None:
        with self.repo.transaction():
            self.repo.con.execute(
                "UPDATE worker_lease SET heartbeat_at=? WHERE owner_id=? AND generation=?",
                (self.repo.clock.now().isoformat(), self.owner, self.generation),
            )

    async def tick(self) -> bool:
        if not self.acquire():
            return False
        executor = Executor(self.repo, self.settings, self.owner, self.generation, self.checkpoint)
        try:
            row = self.repo.con.execute(
                "SELECT id FROM cases WHERE reconcile_requested=1 LIMIT 1"
            ).fetchone()
            if row:
                with self.repo.transaction():
                    executor.fence()
                    self.repo.con.execute(
                        "UPDATE cases SET reconcile_requested=0 WHERE id=?", (row[0],)
                    )
                for op in self.repo.get_case(row[0]).operations:
                    if op.state == "unknown":
                        await executor.reconcile_operation(op)
                return True
            for case in self.repo.list_cases():
                if case.state == "new":
                    await Workflow(self.repo, self.settings, self.model).gather(case.id)
                    return True
                if case.state in {"approved", "executing"}:
                    op = await executor.claim_next(case.id, self.owner, self.generation)
                    if op:
                        await executor.send(op)
                        if self.repo.get_case(case.id).state == "review_required":
                            await executor.reconcile_operation(
                                self.repo.get_case(case.id).operations[op.ordinal - 1]
                            )
                        return True
        except (DependencyError, Fenced):
            return False
        return False

    async def close(self) -> None:
        with self.repo.transaction():
            self.repo.con.execute(
                "UPDATE worker_lease SET heartbeat_at=? WHERE owner_id=? AND generation=?",
                (
                    (self.repo.clock.now() - timedelta(seconds=31)).isoformat(),
                    self.owner,
                    self.generation,
                ),
            )
