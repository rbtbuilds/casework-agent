import asyncio
import os
import socket
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import httpx

ROOT = Path(__file__).resolve().parents[1]
PORTS = {"orders": 8212, "carrier": 8312, "tickets": 8412, "app": 8112}

@dataclass
class Counts:
    tickets: int
    annotations: int

class TestSystem:
    __test__ = False
    def __init__(self, root: Path) -> None:
        self.root = root
        self.processes: dict[str, subprocess.Popen[bytes]] = {}
        self.logs: list[object] = []
        self.api = httpx.AsyncClient(base_url="http://127.0.0.1:8112", timeout=5)
        self.orders = httpx.AsyncClient(base_url="http://127.0.0.1:8212", timeout=5)
        self.carrier = httpx.AsyncClient(base_url="http://127.0.0.1:8312", timeout=5)
        self.ticket = httpx.AsyncClient(base_url="http://127.0.0.1:8412", timeout=5)
    async def __aenter__(self) -> Self:
        return self
    async def __aexit__(self, *args: object) -> None:
        await self.stop()
    async def spawn(self, name: str, module: str, extra: list[str] | None = None) -> None:
        port = PORTS[name]
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} is already owned; refusing")
        self.root.mkdir(parents=True, exist_ok=True)
        log = (self.root / f"{name}.log").open("wb")
        env = dict(os.environ, CASEWORK_ROOT=str(self.root))
        proc = subprocess.Popen([sys.executable, "-m", module, "--root", str(self.root), "--port", str(port), *(extra or [])], cwd=ROOT, stdout=log, stderr=log, env=env)
        log.close()
        self.processes[name] = proc
        async with httpx.AsyncClient() as client:
            for _ in range(80):
                if proc.poll() is not None:
                    raise RuntimeError(f"{name} exited: {(self.root / f'{name}.log').read_text()[-1500:]}")
                try:
                    if (await client.get(f"http://127.0.0.1:{port}/health")).status_code == 200:
                        return
                except httpx.TransportError:
                    pass
                await asyncio.sleep(0.05)
        raise RuntimeError(f"{name} did not start")
    async def start(self, ticket_drop_after_commit: bool = False, app: bool = False) -> None:
        await self.spawn("orders", "mocks.orders")
        await self.spawn("carrier", "mocks.carrier")
        await self.spawn("tickets", "mocks.tickets", ["--drop-after-commit"] if ticket_drop_after_commit else [])
        if app:
            await self.spawn("app", "casework_agent.cli")
    async def stop_process(self, name: str) -> None:
        proc = self.processes.pop(name, None)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                await asyncio.to_thread(proc.wait, 5)
            except subprocess.TimeoutExpired:
                proc.kill()
                await asyncio.to_thread(proc.wait)
    async def stop(self) -> None:
        for name in list(reversed(self.processes)):
            await self.stop_process(name)
        for client in [self.api, self.orders, self.carrier, self.ticket]:
            await client.aclose()

    async def counts(self) -> Counts:
        def count(name: str,table: str) -> int:
            with sqlite3.connect(self.root/f"{name}.sqlite3") as con:
                return int(con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        return Counts(count("tickets","tickets"),count("orders","annotations"))
