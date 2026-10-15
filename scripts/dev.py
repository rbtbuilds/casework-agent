"""Own only this project's exact subprocess identities on the reserved ports."""

import argparse
import json
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import httpx
import psutil
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
PORTS = {"orders": 8212, "carrier": 8312, "tickets": 8412, "app": 8112, "web": 5112}


class Child(BaseModel):
    name: str
    pid: int
    created: float
    argv: list[str]
    nonce: str


def matching(child: Child) -> psutil.Process | None:
    try:
        process = psutil.Process(child.pid)
        if (
            process.create_time() != child.created
            or process.cmdline() != child.argv
            or process.environ().get("CASEWORK_OWNER") != child.nonce
        ):
            raise RuntimeError(
                f"Ownership differs for {child.name}; refusing to stop PID {child.pid}"
            )
        return process
    except psutil.NoSuchProcess:
        return None


def stop_children(children: list[Child]) -> None:
    for child in reversed(children):
        process = matching(child)
        if process:
            process.terminate()
            try:
                process.wait(8)
            except psutil.TimeoutExpired:
                process = matching(child)
                if process:
                    process.kill()
                    process.wait(5)


def start(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    manifest = root / "processes.json"
    if manifest.exists():
        previous = [
            Child.model_validate(v) for v in cast(list[object], json.loads(manifest.read_text()))
        ]
        if any(matching(child) for child in previous):
            raise RuntimeError("Owned services are already running; use status or stop.")
    for port in PORTS.values():
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} is occupied; no process changed.")
    node = shutil.which("node")
    if not node or not (ROOT / "web/node_modules/vite/bin/vite.js").exists():
        raise RuntimeError("Install locked web dependencies first.")
    if os.environ.get("CASEWORK_TEST_CLOCK") == "1" and not (root / "clock.txt").exists():
        (root / "clock.txt").write_text(datetime.now(UTC).isoformat())
    nonce = secrets.token_hex(16)
    children: list[Child] = []
    try:
        for name, port in PORTS.items():
            if name == "web":
                args = [
                    node,
                    str(ROOT / "web/node_modules/vite/bin/vite.js"),
                    "--config",
                    str(ROOT / "web/vite.config.ts"),
                ]
                cwd = ROOT / "web"
            else:
                module = "casework_agent.cli" if name == "app" else f"mocks.{name}"
                args = [sys.executable, "-m", module, "--root", str(root), "--port", str(port)]
                if name == "orders" and os.environ.get("CASEWORK_TEST_DROP_ORDER") == "1":
                    args.append("--drop-after-commit")
                if name == "tickets" and os.environ.get("CASEWORK_TEST_DROP_TICKET") == "1":
                    args.append("--drop-after-commit")
                cwd = ROOT
            with (root / f"{name}.log").open("ab") as log:
                proc = subprocess.Popen(
                    args,
                    cwd=cwd,
                    env=dict(os.environ, CASEWORK_OWNER=nonce),
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
            process = psutil.Process(proc.pid)
            child = Child(
                name=name,
                pid=proc.pid,
                created=process.create_time(),
                argv=process.cmdline(),
                nonce=nonce,
            )
            children.append(child)
            manifest.write_text(json.dumps([c.model_dump() for c in children], indent=2))
            url = f"http://127.0.0.1:{port}" + ("/" if name == "web" else "/health")
            for _ in range(100):
                if proc.poll() is not None:
                    raise RuntimeError(f"{name} exited; read {root / (name + '.log')}")
                try:
                    if httpx.get(url, timeout=0.5).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError(f"{name} readiness timeout")
        print(f"Workbench: http://127.0.0.1:5112; owner record: {manifest}")
    except BaseException:
        stop_children(children)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "run", "stop", "status"])
    parser.add_argument("--root", type=Path, default=ROOT / ".runtime/dev")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_relative_to((ROOT / ".runtime").resolve()):
        raise ValueError("Lifecycle roots must stay inside this project .runtime")
    if args.command in {"start", "run"}:
        start(root)
        if args.command == "run":

            def interrupted(_signum: int, _frame: object) -> None:
                raise KeyboardInterrupt

            signal.signal(signal.SIGTERM, interrupted)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                children = [
                    Child.model_validate(v)
                    for v in cast(list[object], json.loads((root / "processes.json").read_text()))
                ]
                stop_children(children)
    else:
        manifest = root / "processes.json"
        children = (
            [Child.model_validate(v) for v in cast(list[object], json.loads(manifest.read_text()))]
            if manifest.exists()
            else []
        )
        if args.command == "stop":
            stop_children(children)
            print("Verified owned services stopped.")
        else:
            for child in children:
                print(f"{child.name}: {child.pid} {'running' if matching(child) else 'stopped'}")


if __name__ == "__main__":
    main()
