import asyncio
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import cast

from scripts.dev import Child, matching, stop_children
from tests.support import ROOT


async def test_sigterm_during_readiness_stops_owned_children(tmp_path: Path) -> None:
    root = tmp_path / "interrupted-start"
    script = (
        "import sys,time;from scripts import dev;"
        "dev.httpx.get=lambda *a,**k: time.sleep(30);"
        "sys.argv=['dev.py','run','--root',sys.argv[1]];dev.main()"
    )
    with (tmp_path / "supervisor.log").open("wb") as log:
        process = await asyncio.to_thread(
            subprocess.Popen,
            [sys.executable, "-c", script, str(root)],
            cwd=ROOT,
            stdout=log,
            stderr=log,
            env=dict(os.environ),
        )
    children: list[Child] = []
    try:
        for _ in range(100):
            manifest = root / "processes.json"
            if manifest.exists():
                children = [
                    Child.model_validate(v)
                    for v in cast(list[object], json.loads(manifest.read_text()))
                ]
                break
            if process.poll() is not None:
                raise AssertionError((tmp_path / "supervisor.log").read_text())
            await asyncio.sleep(0.05)
        assert children, "Supervisor did not record its first child"
        process.send_signal(signal.SIGTERM)
        await asyncio.to_thread(process.wait, 10)
        assert not any(matching(child) for child in children)
    finally:
        if process.poll() is None:
            process.terminate()
            await asyncio.to_thread(process.wait, 10)
        await asyncio.to_thread(stop_children, children)


async def test_sigterm_between_spawn_and_registration_stops_the_new_child(tmp_path: Path) -> None:
    root = tmp_path / "interrupted-registration"
    script = """
import json,os,signal,sys
from pathlib import Path
from scripts import dev
root=Path(sys.argv[1])
original=dev.subprocess.Popen
original_kill=dev.psutil.Process.kill

def tracked_kill(process):
    (root/'forced-kill').touch()
    return original_kill(process)

dev.psutil.Process.kill=tracked_kill

def interrupted_spawn(*args,**kwargs):
    proc=original(*args,**kwargs)
    process=dev.psutil.Process(proc.pid)
    child=dev.Child(name='orders',pid=proc.pid,created=process.create_time(),argv=process.cmdline(),nonce=kwargs['env']['CASEWORK_OWNER'])
    (root/'spawned.json').write_text(child.model_dump_json())
    os.kill(os.getpid(),signal.SIGTERM)
    return proc

dev.subprocess.Popen=interrupted_spawn
sys.argv=['dev.py','run','--root',str(root)]
dev.main()
"""
    with (tmp_path / "registration.log").open("wb") as log:
        process = await asyncio.to_thread(
            subprocess.Popen,
            [sys.executable, "-c", script, str(root)],
            cwd=ROOT,
            stdout=log,
            stderr=log,
            env=dict(os.environ),
        )
    children: list[Child] = []
    try:
        await asyncio.to_thread(process.wait, 10)
        children = [Child.model_validate_json((root / "spawned.json").read_text())]
        assert not (root / "forced-kill").exists(), (
            "Child required SIGKILL instead of graceful termination"
        )
        assert not any(matching(child) for child in children)
    finally:
        if process.poll() is None:
            process.terminate()
            await asyncio.to_thread(process.wait, 10)
        if not children and (root / "spawned.json").exists():
            children = [Child.model_validate_json((root / "spawned.json").read_text())]
        await asyncio.to_thread(stop_children, children)
