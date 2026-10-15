import asyncio
from pathlib import Path

import httpx
import pytest

from tests.support import TestSystem

BODY = {"order_id":"o-001","action":"open_investigation","queue":"delivery_investigation","priority":"normal","internal_note":"Fictional delayed delivery."}

async def test_ticket_retry_after_drop_has_one_effect(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start(ticket_drop_after_commit=True)
        headers={"Idempotency-Key":"test-ticket-retry"}
        with pytest.raises(httpx.TransportError):
            await system.ticket.post("/v1/tickets",json=BODY,headers=headers)
        replay=await system.ticket.post("/v1/tickets",json=BODY,headers=headers)
        assert replay.status_code==201
        journal=await system.ticket.get("/v1/operations/test-ticket-retry")
        assert journal.json()["response_json"]["ticket_id"]==replay.json()["ticket_id"]
        conflict=await system.ticket.post("/v1/tickets",json={**BODY,"internal_note":"Changed"},headers=headers)
        assert conflict.status_code==409
        assert (await system.counts()).tickets==1

async def test_concurrent_replay_and_annotation_cas(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start()
        replies=await asyncio.gather(*[system.ticket.post("/v1/tickets",json=BODY,headers={"Idempotency-Key":"concurrent"}) for _ in range(6)])
        assert len({r.json()["ticket_id"] for r in replies})==1
        ticket_id=replies[0].json()["ticket_id"]
        body={"order_id":"o-001","ticket_id":ticket_id,"action":"open_investigation","expected_order_version":1}
        headers={"Idempotency-Key":"annotation"}
        first=await system.orders.post("/v1/orders/o-001/annotations",json=body,headers=headers)
        second=await system.orders.post("/v1/orders/o-001/annotations",json=body,headers=headers)
        assert first.status_code==201 and first.json()==second.json()
        assert (await system.orders.get("/v1/orders/o-001")).json()["version"]==2
        rejected=await system.orders.post("/v1/orders/o-001/annotations",json=body,headers={"Idempotency-Key":"stale"})
        assert rejected.status_code==409
        assert (await system.orders.get("/v1/operations/stale")).json()["outcome"]=="rejected"
