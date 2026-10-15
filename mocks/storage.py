import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from casework_agent.contracts import (
    JournalResult,
    JsonDict,
    Order,
    OrderAnnotation,
    Shipment,
    Ticket,
    uid,
)
from casework_agent.hashing import canonical_hash

from .contracts import AnnotationCreate, TicketCreate


class MockStore:
    def __init__(self, path: Path, order: Order, shipment: Shipment) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(path, isolation_level=None, check_same_thread=False, timeout=5)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.executescript("""
        CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_migrations VALUES(1);
        CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS shipments(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tickets(id TEXT PRIMARY KEY,payload TEXT NOT NULL,operation_key TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS annotations(id TEXT PRIMARY KEY,payload TEXT NOT NULL,operation_key TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS idempotency(key TEXT PRIMARY KEY,request_hash TEXT NOT NULL,payload TEXT NOT NULL);
        """)
        self.con.execute(
            "INSERT OR IGNORE INTO orders VALUES(?,?)", (order.order_id, order.model_dump_json())
        )
        self.con.execute(
            "INSERT OR IGNORE INTO shipments VALUES(?,?)",
            (shipment.shipment_id, shipment.model_dump_json()),
        )

    def order(self, id: str) -> Order:
        row = self.con.execute("SELECT payload FROM orders WHERE id=?", (id,)).fetchone()
        if row is None:
            raise KeyError(id)
        return Order.model_validate_json(str(row[0]))

    def shipment(self, id: str) -> Shipment:
        row = self.con.execute("SELECT payload FROM shipments WHERE id=?", (id,)).fetchone()
        if row is None:
            raise KeyError(id)
        return Shipment.model_validate_json(str(row[0]))

    def journal(self, key: str) -> JournalResult | None:
        row = self.con.execute("SELECT payload FROM idempotency WHERE key=?", (key,)).fetchone()
        return None if row is None else JournalResult.model_validate_json(str(row[0]))

    def mutate(self, key: str, body: TicketCreate | AnnotationCreate) -> tuple[int, JsonDict, bool]:
        fingerprint = canonical_hash(body.model_dump(mode="json"))
        self.con.execute("BEGIN IMMEDIATE")
        try:
            prior = self.journal(key)
            if prior:
                self.con.execute("COMMIT")
                if prior.request_hash != fingerprint:
                    return 409, {"error": {"code": "idempotency_conflict"}}, True
                return prior.http_status, prior.response_json, True
            status = 201
            result: JsonDict
            if isinstance(body, TicketCreate):
                expected = (
                    "delivery_investigation"
                    if body.action == "open_investigation"
                    else "human_review"
                )
                if body.queue != expected:
                    status = 409
                    result = {"error": {"code": "policy_conflict"}}
                else:
                    ticket = Ticket(ticket_id=uid(), **body.model_dump(), operation_key=key)
                    self.con.execute(
                        "INSERT INTO tickets VALUES(?,?,?)",
                        (ticket.ticket_id, ticket.model_dump_json(), key),
                    )
                    result = cast(JsonDict, ticket.model_dump(mode="json"))
            else:
                order = self.order(body.order_id)
                if order.version != body.expected_order_version:
                    status = 409
                    result = {"error": {"code": "version_conflict"}}
                else:
                    annotation = OrderAnnotation(
                        annotation_id=uid(),
                        ticket_id=body.ticket_id,
                        action=body.action,
                        operation_key=key,
                    )
                    order.annotations.append(annotation)
                    order.version += 1
                    self.con.execute(
                        "UPDATE orders SET payload=? WHERE id=?",
                        (order.model_dump_json(), order.order_id),
                    )
                    self.con.execute(
                        "INSERT INTO annotations VALUES(?,?,?)",
                        (annotation.annotation_id, annotation.model_dump_json(), key),
                    )
                    result = cast(JsonDict, annotation.model_dump(mode="json"))
            journal = JournalResult(
                key=key,
                request_hash=fingerprint,
                outcome="succeeded" if status == 201 else "rejected",
                http_status=status,
                response_json=result,
                committed_at=datetime.now(UTC),
            )
            self.con.execute(
                "INSERT INTO idempotency VALUES(?,?,?)",
                (key, fingerprint, journal.model_dump_json()),
            )
            self.con.execute("COMMIT")
            return status, result, False
        except BaseException:
            self.con.execute("ROLLBACK")
            raise
