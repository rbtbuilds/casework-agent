import argparse
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

import uvicorn
from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from starlette.middleware.base import RequestResponseEndpoint

from casework_agent.contracts import Order, Shipment

from .contracts import AnnotationCreate, TicketCreate
from .faults import FaultConfig
from casework_agent.hashing import canonical_json
from .storage import MockStore

type ServiceKind = Literal["orders","carrier","tickets"]

async def dropped_body() -> AsyncGenerator[bytes,None]:
    yield b"{"
    raise RuntimeError("Intentional fictional fault: response lost after commit")

def create_service(kind: ServiceKind,root: Path,faults: FaultConfig | None=None) -> FastAPI:
    fault=faults or FaultConfig()
    seed_file=root/"scenario.json"
    if not seed_file.exists():seed_file=Path(__file__).resolve().parents[1]/"fixtures/scenarios/dev-delay-01.json"
    seed=json.loads(seed_file.read_text())
    store=MockStore(root/f"{kind}.sqlite3",Order.model_validate(seed["order"]),Shipment.model_validate(seed["shipment"]))
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None,None]:
        yield
        store.con.close()
    app=FastAPI(title=f"Fictional {kind}",lifespan=lifespan)
    @app.middleware("http")
    async def safety(request: Request,call_next: RequestResponseEndpoint) -> Response:
        origin=request.headers.get("origin")
        if origin and origin!="http://127.0.0.1:5112":return JSONResponse({"error":{"code":"origin_rejected"}},status_code=403)
        raw=await request.body()
        if len(raw)>32768:return JSONResponse({"error":{"code":"body_too_large"}},status_code=413)
        return await call_next(request)
    # Routes use a single event loop; no transaction spans an await.
    @app.get("/health")
    async def health() -> dict[str,str]:return {"status":"ok"}
    @app.get("/v1/orders/{id}")
    async def get_order(id: str) -> Response:
        if fault.fail_reads>0:
            fault.fail_reads-=1
            return JSONResponse({"error":{"code":"injected_read_failure"}},status_code=503)
        try:return JSONResponse(store.order(id).model_dump(mode="json"))
        except KeyError:return JSONResponse({"error":{"code":"not_found"}},status_code=404)
    @app.get("/v1/shipments/{id}")
    async def get_shipment(id: str) -> Response:
        if fault.fail_reads>0:
            fault.fail_reads-=1
            return JSONResponse({"error":{"code":"injected_read_failure"}},status_code=503)
        try:return JSONResponse(store.shipment(id).model_dump(mode="json"))
        except KeyError:return JSONResponse({"error":{"code":"not_found"}},status_code=404)
    @app.get("/v1/operations/{key}")
    async def journal(key: str) -> Response:
        value=store.journal(key)
        return JSONResponse(value.model_dump(mode="json") if value else {"error":{"code":"not_found"}},status_code=200 if value else 404)
    def mutation(key: str,body: TicketCreate | AnnotationCreate) -> Response:
        if not key or len(key)>160 or not key.isascii():return JSONResponse({"error":{"code":"invalid_key"}},status_code=400)
        status,result,replayed=store.mutate(key,body)
        if fault.drop_after_commit and not replayed and status==201:
            return StreamingResponse(dropped_body(),status_code=201,media_type="application/json",headers={"Content-Length":str(len(canonical_json(result).encode()))})
        return JSONResponse(result,status_code=status)
    if kind=="tickets":
        @app.post("/v1/tickets")
        async def ticket(body: TicketCreate,idempotency_key: Annotated[str,Header()]) -> Response:
            return mutation(idempotency_key,body)
        @app.get("/v1/tickets/{id}")
        async def get_ticket(id: str) -> Response:
            row=store.con.execute("SELECT payload FROM tickets WHERE id=?",(id,)).fetchone()
            return JSONResponse(json.loads(str(row[0])) if row else {"error":{"code":"not_found"}},status_code=200 if row else 404)
    if kind=="orders":
        @app.post("/v1/orders/{id}/annotations")
        async def annotation(id: str,body: AnnotationCreate,idempotency_key: Annotated[str,Header()]) -> Response:
            if body.order_id!=id:return JSONResponse({"error":{"code":"order_mismatch"}},status_code=409)
            return mutation(idempotency_key,body)
    return app

def main(kind: ServiceKind) -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--port",type=int,required=True)
    parser.add_argument("--drop-after-commit",action="store_true")
    parser.add_argument("--fail-reads",type=int,default=0)
    args=parser.parse_args()
    uvicorn.run(create_service(kind,args.root,FaultConfig(drop_after_commit=args.drop_after_commit,fail_reads=args.fail_reads)),host="127.0.0.1",port=args.port,log_level="warning")
