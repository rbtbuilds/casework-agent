import asyncio
import contextlib
import json
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .config import Settings
from .contracts import ApiError, ApprovalRequest, CaseSeed, CaseView, VersionRequest
from .model_session import snapshot
from .repository import Conflict, Repository
from .tools import DependencyError
from .worker import Worker
from .workflow import Workflow


class Boundary:
    def __init__(self, app: ASGIApp, origin: str) -> None:
        self.app, self.origin = app, origin

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope["headers"])
        supplied = headers.get(b"origin")
        code, status = "", 0
        if supplied is not None and supplied.decode("latin1") != self.origin:
            code, status = "origin_rejected", 403
        elif (
            scope["method"] == "POST"
            and headers.get(b"content-type", b"").split(b";")[0] != b"application/json"
        ):
            code, status = "json_required", 415
        if code:
            await JSONResponse(
                {"error": ApiError(code=code, message=code).model_dump(mode="json")},
                status_code=status,
            )(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > 32768:
                await JSONResponse(
                    {
                        "error": ApiError(
                            code="request_too_large", message="Maximum body size is 32 KiB."
                        ).model_dump(mode="json")
                    },
                    status_code=413,
                )(scope, receive, send)
                return
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        repo = Repository.open(config.database)
        worker = Worker(repo, config)

        async def run() -> None:
            while True:
                await worker.tick()
                await asyncio.sleep(0.1)

        async def heartbeat() -> None:
            while True:
                await asyncio.sleep(5)
                worker.heartbeat()

        tasks = (
            [asyncio.create_task(run()), asyncio.create_task(heartbeat())]
            if config.run_worker
            else []
        )
        try:
            yield
        finally:
            for task in tasks:
                task.cancel()
            for task in tasks:
                with contextlib.suppress(asyncio.CancelledError):
                    await task
            await worker.close()
            repo.close()

    app = FastAPI(title="Casework Agent", version="0.1.0", lifespan=lifespan)
    app.add_middleware(Boundary, origin=config.web_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.web_origin],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Idempotency-Key"],
    )

    async def repository() -> AsyncIterator[Repository]:
        with Repository.open(config.database) as repo:
            yield repo

    async def key(value: Annotated[str, Header(alias="Idempotency-Key")]) -> str:
        if (
            not 1 <= len(value) <= 160
            or not value.isascii()
            or any(ord(c) < 33 or ord(c) > 126 for c in value)
        ):
            raise Conflict("invalid_idempotency_key", 422)
        return value

    @app.exception_handler(Conflict)
    async def conflict(_request: Request, exc: Conflict) -> JSONResponse:
        return JSONResponse(
            {"error": ApiError(code=exc.code, message=exc.code).model_dump(mode="json")},
            status_code=exc.status,
        )

    @app.exception_handler(KeyError)
    async def missing(_request: Request, _exc: KeyError) -> JSONResponse:
        return JSONResponse(
            {
                "error": ApiError(code="not_found", message="Case not found.").model_dump(
                    mode="json"
                )
            },
            status_code=404,
        )

    @app.exception_handler(DependencyError)
    async def dependency(_request: Request, _exc: DependencyError) -> JSONResponse:
        return JSONResponse(
            {
                "error": ApiError(
                    code="dependency_unavailable",
                    message="Fresh evidence could not be read; no approval was created.",
                    retryable=True,
                ).model_dump(mode="json")
            },
            status_code=503,
        )

    @app.exception_handler(RequestValidationError)
    async def invalid(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            {
                "error": ApiError(
                    code="validation_error", message="Request does not match the API schema."
                ).model_dump(mode="json")
            },
            status_code=422,
        )

    @app.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            {"error": ApiError(code="http_error", message=str(exc.detail)).model_dump(mode="json")},
            status_code=exc.status_code,
        )

    @app.get("/health")
    async def health(repo: Annotated[Repository, Depends(repository)]) -> dict[str, object]:
        try:
            snapshot(config.model_directory)
            probe = config.model_directory / ".runtime/model-probe.json"
            model = probe.exists() and json.loads(probe.read_text()).get("protocol_valid") is True
        except RuntimeError:
            model = False
        lease = repo.con.execute(
            "SELECT heartbeat_at FROM worker_lease WHERE singleton=1"
        ).fetchone()
        return {
            "status": "ok",
            "schema_version": 1,
            "model_available": model,
            "fixture_available": True,
            "worker_heartbeat": lease[0] if lease else None,
        }

    @app.get("/v1/scenarios")
    async def scenarios() -> list[dict[str, str]]:
        return [
            {
                "scenario_id": "dev-delay-01",
                "order_id": "o-001",
                "as_of": "2026-10-15T12:00:00Z",
                "title": "Delayed delivery example",
            }
        ]

    @app.get("/v1/cases", response_model=list[CaseView])
    async def cases(repo: Annotated[Repository, Depends(repository)]) -> list[CaseView]:
        return repo.list_cases()

    @app.get("/v1/cases/{id}", response_model=CaseView)
    async def case(id: str, repo: Annotated[Repository, Depends(repository)]) -> CaseView:
        return repo.get_case(id)

    @app.post("/v1/cases", response_model=CaseView, status_code=201)
    async def create(
        seed: CaseSeed,
        repo: Annotated[Repository, Depends(repository)],
        token: Annotated[str, Depends(key)],
    ) -> CaseView:
        return repo.create_case(seed, token)

    @app.post("/v1/cases/{id}/decisions", response_model=CaseView)
    async def decide(
        id: str,
        body: ApprovalRequest,
        repo: Annotated[Repository, Depends(repository)],
        token: Annotated[str, Depends(key)],
    ) -> CaseView:
        return await Workflow(repo, config).decide(id, body, token)

    def command_route(action: Literal["cancel", "repropose", "reconcile"]) -> None:
        async def command(
            id: str,
            body: VersionRequest,
            repo: Annotated[Repository, Depends(repository)],
            token: Annotated[str, Depends(key)],
        ) -> CaseView:
            return repo.command(id, action, body, token)

        app.post(
            f"/v1/cases/{{id}}/{action}",
            response_model=CaseView,
            status_code=202 if action == "reconcile" else 200,
            operation_id=action,
        )(command)

    for action in ("cancel", "repropose", "reconcile"):
        command_route(action)
    return app
