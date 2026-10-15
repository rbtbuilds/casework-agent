import asyncio
from datetime import UTC, datetime
from typing import Literal

import httpx
from pydantic import BaseModel

from .config import Settings
from .contracts import Evidence, Order, Policy, Shipment
from .hashing import canonical_hash
from .policy import current_policy


class ToolPermissionError(ValueError):pass
class DependencyError(RuntimeError):pass

class ReadTools:
    def __init__(self,case_id: str,order_id: str,settings: Settings) -> None:
        self.case_id,self.order_id,self.settings=case_id,order_id,settings
        self.client=httpx.AsyncClient(timeout=2,follow_redirects=False)
        self.evidence: list[Evidence]=[]
        self.order: Order | None=None
        self.shipment: Shipment | None=None
        self.request_count=0
        self.calls=0
    async def close(self) -> None:await self.client.aclose()
    async def read[T: BaseModel](self,url: str,cls: type[T]) -> T:
        for attempt in range(3):
            self.request_count+=1
            try:
                response=await self.client.get(url)
                response.raise_for_status()
                if len(response.content)>32768:raise DependencyError("oversized_response")
                return cls.model_validate_json(response.content)
            except (httpx.HTTPError,ValueError) as exc:
                if attempt==2:raise DependencyError("read_failed") from exc
                await asyncio.sleep([0.1,0.3][attempt])
        raise DependencyError("read_failed")
    def record(self,source: Literal["order","carrier","policy"],source_id: str,version: str,payload: Order | Shipment | Policy) -> Evidence:
        self.calls+=1
        if self.calls>8:raise ToolPermissionError("tool_budget_exhausted")
        evidence=Evidence(case_id=self.case_id,source=source,source_id=source_id,source_version=version,payload=payload,payload_hash=canonical_hash(payload.model_dump(mode="json")),fetched_at=datetime.now(UTC))
        self.evidence.append(evidence)
        return evidence
    async def get_order(self,order_id: str) -> Evidence:
        if order_id!=self.order_id:raise ToolPermissionError("order_scope")
        from urllib.parse import quote
        self.order=await self.read(f"{self.settings.orders_url}/v1/orders/{quote(order_id,safe='')}",Order)
        if self.order.order_id!=order_id:raise ToolPermissionError("order_response_scope")
        return self.record("order",order_id,str(self.order.version),self.order)
    async def get_shipment(self,shipment_id: str) -> Evidence:
        if self.order is None or shipment_id!=self.order.shipment_id:raise ToolPermissionError("shipment_scope")
        from urllib.parse import quote
        self.shipment=await self.read(f"{self.settings.carrier_url}/v1/shipments/{quote(shipment_id,safe='')}",Shipment)
        if self.shipment.shipment_id!=shipment_id:raise ToolPermissionError("shipment_response_scope")
        return self.record("carrier",shipment_id,str(self.shipment.version),self.shipment)
    async def get_policy(self) -> Evidence:
        policy=current_policy()
        return self.record("policy",policy.version,policy.hash,policy)
