import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import cast
from urllib.parse import quote

import httpx

from .config import Settings
from .contracts import Approval, JournalResult, JsonDict, Operation, OrderAnnotation, Ticket
from .hashing import canonical_hash
from .http import bounded_request
from .policy import current_policy
from .repository import Repository
from .tools import ReadTools


class Fenced(RuntimeError):
    pass


class Executor:
    def __init__(
        self,
        repo: Repository,
        settings: Settings,
        owner: str,
        generation: int,
        checkpoint: Callable[[str], None] | None = None,
    ) -> None:
        self.repo, self.settings, self.owner, self.generation = repo, settings, owner, generation
        self.checkpoint: Callable[[str], None] = checkpoint or self.no_checkpoint

    @staticmethod
    def no_checkpoint(_name: str) -> None:
        pass

    def fence(self) -> None:
        row = self.repo.con.execute("SELECT * FROM worker_lease WHERE singleton=1").fetchone()
        if (
            not row
            or row["owner_id"] != self.owner
            or row["generation"] != self.generation
            or datetime.fromisoformat(row["heartbeat_at"])
            <= self.repo.clock.now() - timedelta(seconds=30)
        ):
            raise Fenced("worker_fenced")

    async def claim_next(self, case_id: str, owner_id: str, generation: int) -> Operation | None:
        if owner_id != self.owner or generation != self.generation:
            raise Fenced("worker_fenced")
        case = self.repo.get_case(case_id)
        if case.state not in {"approved", "executing"} or not case.proposal:
            return None
        pending = next((o for o in case.operations if o.state == "pending"), None)
        if not pending:
            return None
        order_version, shipment_version = (
            case.proposal.order_version,
            case.proposal.shipment_version,
        )
        if pending.ordinal == 1:
            tools = ReadTools(case_id, case.order_id, self.settings)
            try:
                await tools.get_order(case.order_id)
                assert tools.order
                await tools.get_shipment(tools.order.shipment_id)
                assert tools.shipment
                order_version, shipment_version = tools.order.version, tools.shipment.version
            finally:
                await tools.close()
        with self.repo.transaction():
            self.fence()
            case = self.repo.get_case(case_id)
            if case.state not in {"approved", "executing"}:
                return None
            p = case.proposal
            assert p
            op = next(o for o in case.operations if o.id == pending.id)
            if op.state != "pending":
                return None
            approval_row = self.repo.con.execute(
                "SELECT payload_json FROM approvals WHERE id=?", (op.approval_id,)
            ).fetchone()
            approval = Approval.model_validate_json(approval_row[0]) if approval_row else None
            if (
                not approval
                or approval.decision != "approve"
                or approval.proposal_id != p.id
                or approval.proposal_hash != p.hash
            ):
                raise Fenced("approval_missing")
            if op.ordinal == 1:
                if (
                    p.expires_at <= self.repo.clock.now()
                    or p.order_version != order_version
                    or p.shipment_version != shipment_version
                    or p.policy_hash != canonical_hash(current_policy().model_dump(mode="json"))
                ):
                    self.repo.invalidate(case_id, "stale_before_claim")
                    return None
                body: JsonDict = cast(
                    JsonDict, p.intents[0].model_dump(mode="json", exclude={"kind"})
                )
            else:
                ticket = case.operations[0]
                if ticket.state != "succeeded" or not ticket.remote_id:
                    return None
                body = {
                    "order_id": case.order_id,
                    "ticket_id": ticket.remote_id,
                    "action": p.intents[1].action,
                    "expected_order_version": p.intents[1].expected_order_version,
                }
            op.request_json, op.request_hash = body, canonical_hash(body)
            op.attempts += 1
            op.state, op.worker_generation = "in_flight", self.generation
            self.repo.save_operation(op)
            self.repo.transition(case_id, "executing", "operation_claimed")
            self.repo.event(
                case_id,
                "preflight",
                {
                    "order_version": order_version,
                    "shipment_version": shipment_version,
                    "checked_at": self.repo.clock.now().isoformat(),
                    "key": op.key,
                },
            )
        self.checkpoint("before_send")
        return op

    def base(self, op: Operation) -> str:
        return self.settings.tickets_url if op.kind == "create_ticket" else self.settings.orders_url

    def validate_success(self, op: Operation, body: JsonDict) -> str:
        expected = op.request_json
        assert expected
        if op.kind == "create_ticket":
            ticket = Ticket.model_validate(body)
            if ticket.operation_key != op.key or any(body.get(k) != v for k, v in expected.items()):
                raise ValueError("remote_result_mismatch")
            return ticket.ticket_id
        annotation = OrderAnnotation.model_validate(body)
        if (
            annotation.operation_key != op.key
            or annotation.ticket_id != expected["ticket_id"]
            or annotation.action != expected["action"]
        ):
            raise ValueError("remote_result_mismatch")
        return annotation.annotation_id

    def save_result(self, op: Operation, journal: JournalResult) -> None:
        if journal.key != op.key or journal.request_hash != op.request_hash:
            self.unknown(op, "journal_hash_mismatch")
            return
        remote_id = (
            self.validate_success(op, journal.response_json)
            if journal.outcome == "succeeded"
            else None
        )
        with self.repo.transaction():
            self.fence()
            op.state = "succeeded" if journal.outcome == "succeeded" else "rejected"
            op.response_json, op.remote_id, op.last_error = journal.response_json, remote_id, None
            self.repo.save_operation(op)
            case = self.repo.get_case(op.case_id)
            if op.state == "rejected":
                state = (
                    "review_required"
                    if any(o.state == "succeeded" for o in case.operations)
                    else "stale"
                )
            else:
                state = (
                    "completed"
                    if all(o.state == "succeeded" for o in case.operations)
                    else "executing"
                )
            self.repo.transition(case.id, state, f"operation_{op.state}")

    def unknown(self, op: Operation, reason: str) -> None:
        with self.repo.transaction():
            self.fence()
            op.state, op.last_error = "unknown", reason
            self.repo.save_operation(op)
            self.repo.transition(op.case_id, "review_required", "outcome_unconfirmed")

    async def send(self, op: Operation) -> None:
        assert op.request_json and op.request_hash
        url = (
            f"{self.base(op)}/v1/tickets"
            if op.kind == "create_ticket"
            else f"{self.base(op)}/v1/orders/{quote(str(op.request_json['order_id']), safe='')}/annotations"
        )
        try:
            async with httpx.AsyncClient(timeout=3, follow_redirects=False) as client:
                response = await bounded_request(
                    client,
                    "POST",
                    url,
                    body=op.request_json,
                    deadline=3,
                    headers={"Idempotency-Key": op.key},
                )
                self.checkpoint(
                    "ticket_committed_before_local_result"
                    if op.ordinal == 1
                    else "annotation_committed_before_local_result"
                )
                if response.status_code != 201:
                    self.unknown(op, f"mutation_http_{response.status_code}")
                    return
                body = cast(JsonDict, response.json())
                self.validate_success(op, body)
                result = JournalResult(
                    key=op.key,
                    request_hash=op.request_hash,
                    outcome="succeeded",
                    http_status=201,
                    response_json=body,
                    committed_at=self.repo.clock.now(),
                )
                self.save_result(op, result)
        except (httpx.HTTPError, ValueError, TimeoutError) as exc:
            self.unknown(op, type(exc).__name__)

    async def reconcile_operation(self, op: Operation) -> None:
        async with httpx.AsyncClient(timeout=3, follow_redirects=False) as client:
            for attempt in range(3):
                try:
                    response = await bounded_request(
                        client,
                        "GET",
                        f"{self.base(op)}/v1/operations/{quote(op.key, safe='')}",
                        deadline=3,
                    )
                    if response.status_code == 404:
                        if op.attempts < 3:
                            with self.repo.transaction():
                                self.fence()
                                op.attempts += 1
                                op.state, op.worker_generation = "in_flight", self.generation
                                self.repo.save_operation(op)
                                self.repo.transition(
                                    op.case_id, "executing", "identical_replay_claimed"
                                )
                            await self.send(op)
                        else:
                            self.unknown(op, "send_budget_exhausted")
                        return
                    response.raise_for_status()
                    journal = JournalResult.model_validate_json(response.content)
                    self.save_result(op, journal)
                    return
                except (httpx.HTTPError, ValueError, TimeoutError):
                    if attempt < 2:
                        await asyncio.sleep([0.1, 0.3][attempt])
            self.unknown(op, "journal_unavailable")
