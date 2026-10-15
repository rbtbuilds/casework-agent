import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Literal, Self, cast

from .clock import Clock, SystemClock
from .contracts import (
    AgentDecision,
    ApiError,
    Approval,
    ApprovalRequest,
    AuditEvent,
    CaseSeed,
    CaseState,
    CaseView,
    Evidence,
    JsonDict,
    Operation,
    Proposal,
    VersionRequest,
    uid,
)
from .db import connect
from .hashing import canonical_hash, canonical_json
from .policy import compile_intents
from .tools import ReadTools


class Conflict(ValueError):
    def __init__(self, code: str, status: int = 409) -> None:
        self.code = code
        self.status = status
        super().__init__(code)


class Repository:
    def __init__(self, path: Path, clock: Clock | None = None) -> None:
        self.path = path
        self.clock = clock or SystemClock()
        self.con = connect(path)

    @classmethod
    def open(cls, path: Path, clock: Clock | None = None) -> Self:
        return cls(path, clock)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self.con.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        self.con.execute("BEGIN IMMEDIATE")
        try:
            yield self.con
            self.con.execute("COMMIT")
        except BaseException:
            self.con.execute("ROLLBACK")
            raise

    def event(self, id: str, kind: str, payload: JsonDict | None = None) -> None:
        self.con.execute("INSERT INTO audit_events(case_id,kind,payload_json,created_at) VALUES(?,?,?,?)", (id, kind, canonical_json(payload or {}), self.clock.now().isoformat()))

    def transition(self, id: str, state: CaseState, kind: str, error: ApiError | None = None) -> None:
        self.con.execute("UPDATE cases SET state=?,version=version+1,error_json=?,updated_at=? WHERE id=?", (state, error.model_dump_json() if error else None, self.clock.now().isoformat(), id))
        self.event(id, kind)

    def replay(self, key: str, fingerprint: str) -> CaseView | None:
        row = self.con.execute("SELECT * FROM api_idempotency WHERE key=?", (key,)).fetchone()
        if row is None:
            return None
        if row["fingerprint"] != fingerprint:
            raise Conflict("idempotency_conflict")
        return CaseView.model_validate_json(row["response_json"])

    def remember(self, key: str, fingerprint: str, case: CaseView, status: int = 200) -> None:
        self.con.execute("INSERT INTO api_idempotency VALUES(?,?,?,?,?)", (key, fingerprint, status, case.model_dump_json(), self.clock.now().isoformat()))

    def create_case(self, seed: CaseSeed, key: str | None = None) -> CaseView:
        fingerprint = canonical_hash(["create", seed.model_dump(mode="json")])
        with self.transaction():
            if key and (cached := self.replay(key, fingerprint)):
                return cached
            id, now = uid(), self.clock.now().isoformat()
            self.con.execute("INSERT INTO cases(id,seed_json,state,version,created_at,updated_at) VALUES(?,?,'new',1,?,?)", (id, seed.model_dump_json(), now, now))
            self.event(id, "case_created", {"mode": seed.mode})
            case = self.get_case(id)
            if key:
                self.remember(key, fingerprint, case, 201)
            return case

    def list_cases(self) -> list[CaseView]:
        return [self.get_case(row[0]) for row in self.con.execute("SELECT id FROM cases ORDER BY created_at DESC")]

    def get_case(self, id: str) -> CaseView:
        row = self.con.execute("SELECT * FROM cases WHERE id=?", (id,)).fetchone()
        if row is None:
            raise KeyError(id)
        seed = CaseSeed.model_validate_json(row["seed_json"])
        p = self.con.execute("SELECT payload_json FROM proposals WHERE id=?", (row["proposal_id"],)).fetchone()
        proposal = Proposal.model_validate_json(p[0]) if p else None
        operations = [Operation.model_validate_json(o[0]) for o in self.con.execute("SELECT payload_json FROM operations WHERE case_id=? ORDER BY ordinal", (id,))]
        evidence = [Evidence.model_validate_json(e[0]) for e in self.con.execute("SELECT payload_json FROM evidence WHERE case_id=?", (id,))]
        events = [AuditEvent(id=e["id"], case_id=id, kind=e["kind"], payload=json.loads(e["payload_json"]), created_at=e["created_at"]) for e in self.con.execute("SELECT * FROM audit_events WHERE case_id=? ORDER BY id", (id,))]
        actions: list[Literal["approve", "reject", "cancel", "repropose", "reconcile"]] = []
        state = row["state"]
        sent = any(o.attempts > 0 for o in operations)
        if state == "needs_approval" and proposal and proposal.expires_at > self.clock.now():
            actions.extend(["approve", "reject"])
        if state in {"new", "gathering", "needs_approval", "approved"} and not sent:
            actions.append("cancel")
        if state in {"failed", "stale", "rejected"} and not operations:
            actions.append("repropose")
        if state == "review_required" and any(o.state == "unknown" for o in operations):
            actions.append("reconcile")
        return CaseView(id=id, **seed.model_dump(), state=state, version=row["version"], proposal=proposal, operations=operations, evidence=evidence, events=events, available_actions=actions, error=ApiError.model_validate_json(row["error_json"]) if row["error_json"] else None)

    def begin_gather(self, id: str) -> bool:
        with self.transaction():
            if self.get_case(id).state != "new":
                return False
            self.transition(id, "gathering", "gathering_started")
            return True

    def publish(self, id: str, decision: AgentDecision, tools: ReadTools, trace: JsonDict) -> None:
        assert tools.order and tools.shipment
        with self.transaction():
            if self.get_case(id).state != "gathering":
                return
            now = self.clock.now()
            version = self.con.execute("SELECT COALESCE(MAX(version),0)+1 FROM proposals WHERE case_id=?", (id,)).fetchone()[0]
            policy = next(e for e in tools.evidence if e.source == "policy")
            proposal = Proposal(case_id=id, version=version, policy_hash=policy.payload_hash, evidence_ids=decision.evidence_ids, evidence_hashes=[e.payload_hash for e in tools.evidence if e.id in decision.evidence_ids], order_version=tools.order.version, shipment_version=tools.shipment.version, action=decision.action, rationale=decision.rationale, draft_note=decision.draft_note, intents=compile_intents(decision, tools.order), created_at=now, expires_at=now + timedelta(seconds=900), hash="")
            proposal.hash = canonical_hash(proposal.model_dump(mode="json", exclude={"hash"}))
            for e in tools.evidence:
                self.con.execute("INSERT INTO evidence VALUES(?,?,?,?)", (e.id, id, e.source, e.model_dump_json()))
            self.con.execute("INSERT INTO proposals VALUES(?,?,?,?,?,?,?)", (proposal.id, id, version, proposal.model_dump_json(), proposal.hash, now.isoformat(), proposal.expires_at.isoformat()))
            self.con.execute("INSERT INTO agent_runs VALUES(?,?,?)", (uid(), id, canonical_json(trace)))
            self.con.execute("UPDATE cases SET proposal_id=? WHERE id=?", (proposal.id, id))
            self.transition(id, "needs_approval", "proposal_published")

    def fail_gather(self, id: str, code: str) -> None:
        with self.transaction():
            if self.get_case(id).state == "gathering":
                self.transition(id, "failed", "gathering_failed", ApiError(code=code, message=code, case_id=id))

    def invalidate(self, id: str, code: str) -> None:
        self.con.execute("DELETE FROM operations WHERE case_id=? AND attempts=0 AND state='pending'", (id,))
        self.transition(id, "stale", code, ApiError(code=code, message=code, case_id=id))

    def apply_decision(self, id: str, request: ApprovalRequest, key: str, order_version: int, shipment_version: int, policy_hash: str) -> CaseView:
        fingerprint = canonical_hash(["decision", id, request.model_dump(mode="json")])
        stale = False
        with self.transaction():
            if cached := self.replay(key, fingerprint):
                return cached
            case = self.get_case(id)
            p = case.proposal
            if case.version != request.expected_case_version:
                raise Conflict("case_version_conflict")
            if case.state != "needs_approval" or not p or p.id != request.proposal_id or p.hash != request.proposal_hash:
                raise Conflict("proposal_conflict")
            if p.expires_at <= self.clock.now() or p.policy_hash != policy_hash or p.order_version != order_version or p.shipment_version != shipment_version:
                self.invalidate(id, "stale_proposal")
                stale = True
            else:
                approval = Approval(case_id=id, proposal_id=p.id, proposal_hash=p.hash, decision=request.decision, created_at=self.clock.now())
                self.con.execute("INSERT INTO approvals VALUES(?,?,?,?)", (approval.id, id, p.id, approval.model_dump_json()))
                if request.decision == "approve":
                    for ordinal, kind, suffix in [(1, "create_ticket", "ticket"), (2, "annotate_order", "annotation")]:
                        op = Operation(case_id=id, approval_id=approval.id, ordinal=cast(Literal[1, 2], ordinal), kind=cast(Literal["create_ticket", "annotate_order"], kind), key=f"cw:{id}:{p.version}:{suffix}")
                        self.con.execute("INSERT INTO operations VALUES(?,?,?,?,?,?,?,?)", (op.id, id, ordinal, op.key, op.state, 0, 0, op.model_dump_json()))
                    self.transition(id, "approved", "approved")
                else:
                    self.transition(id, "rejected", "rejected")
                case = self.get_case(id)
                self.remember(key, fingerprint, case)
                return case
        if stale:
            raise Conflict("stale_proposal")
        raise AssertionError("unreachable")

    def command(self, id: str, action: Literal["cancel", "repropose", "reconcile"], request: VersionRequest, key: str) -> CaseView:
        fingerprint = canonical_hash([action, id, request.model_dump(mode="json")])
        with self.transaction():
            if cached := self.replay(key, fingerprint):
                return cached
            case = self.get_case(id)
            if case.version != request.expected_case_version:
                raise Conflict("case_version_conflict")
            if action not in case.available_actions:
                raise Conflict("execution_started" if action == "cancel" and any(o.attempts for o in case.operations) else "action_unavailable")
            if action == "reconcile":
                self.con.execute("UPDATE cases SET reconcile_requested=1 WHERE id=?", (id,))
                self.transition(id, case.state, "reconcile_requested")
            elif action == "cancel":
                self.transition(id, "cancelled", "cancelled")
            else:
                self.transition(id, "new", "reproposal_requested")
            result = self.get_case(id)
            self.remember(key, fingerprint, result, 202 if action == "reconcile" else 200)
            return result

    def save_operation(self, op: Operation) -> None:
        self.con.execute("UPDATE operations SET state=?,attempts=?,worker_generation=?,payload_json=? WHERE id=?", (op.state, op.attempts, op.worker_generation, op.model_dump_json(), op.id))
