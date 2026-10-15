import asyncio
import socket
import sqlite3
import sys
from pathlib import Path
from typing import Self

import httpx

ROOT = Path(__file__).resolve().parents[1]
PORTS = {"orders": 8212, "carrier": 8312, "tickets": 8412}


class Services:
    def __init__(self, root: Path, fault: str) -> None:
        self.root, self.fault = root, fault
        self.processes: dict[str, asyncio.subprocess.Process] = {}

    async def spawn(self, name: str) -> None:
        port = PORTS[name]
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} occupied; refusing.")
        extra = (
            ["--drop-after-commit"]
            if (name == "tickets" and self.fault == "ticket_drop")
            or (name == "orders" and self.fault == "annotation_drop")
            else []
        )
        with (self.root / f"{name}.log").open("ab") as log:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                f"mocks.{name}",
                "--root",
                str(self.root),
                "--port",
                str(port),
                *extra,
                cwd=ROOT,
                stdout=log,
                stderr=log,
            )
        self.processes[name] = proc
        async with httpx.AsyncClient(timeout=0.5) as client:
            for _ in range(100):
                if proc.returncode is not None:
                    raise RuntimeError(f"{name} exited: {self.root}/{name}.log")
                try:
                    if (await client.get(f"http://127.0.0.1:{port}/health")).status_code == 200:
                        return
                except httpx.HTTPError:
                    pass
                await asyncio.sleep(0.05)
        raise RuntimeError(f"{name} not ready")

    async def stop_one(self, name: str) -> None:
        proc = self.processes.pop(name, None)
        if proc and proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), 5)
            except TimeoutError:
                proc.kill()
                await proc.wait()

    async def __aenter__(self) -> Self:
        try:
            for name in PORTS:
                await self.spawn(name)
        except BaseException:
            await self.__aexit__()
            raise
        return self

    async def __aexit__(self, *args: object) -> None:
        for name in list(reversed(self.processes)):
            await self.stop_one(name)

    def counts(self) -> tuple[int, int]:
        with (
            sqlite3.connect(self.root / "tickets.sqlite3") as ticket,
            sqlite3.connect(self.root / "orders.sqlite3") as order,
        ):
            return int(ticket.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]), int(
                order.execute("SELECT COUNT(*) FROM annotations").fetchone()[0]
            )
