import asyncio
import json
import sys
from pathlib import Path

import pytest

from casework_agent.model_adapter import ChatMessage
from casework_agent.model_session import MachineLease, ModelSession


def test_lease_owner_change_is_preserved(tmp_path: Path) -> None:
    lease = MachineLease(tmp_path / "lease")
    lease.acquire("test")
    path = lease.path / "owner.json"
    original = path.read_text()
    path.write_text(json.dumps({"owner_token": "foreign"}))
    with pytest.raises(RuntimeError, match="lease_owner_changed"):
        lease.release()
    assert path.exists()
    path.write_text(original)
    lease.release()


async def test_child_start_failure_releases_only_owned_lease(tmp_path: Path) -> None:
    models = tmp_path / ".runtime/models"
    models.mkdir(parents=True)
    # Empty snapshot reaches the child but cannot load a model; this is a process test, not inference.
    (models / "snapshot.json").write_text(
        json.dumps({"revision": "synthetic", "path": str(models), "files": {}})
    )
    lease = MachineLease(tmp_path / "lease")
    session = ModelSession(tmp_path, lease=lease)
    with pytest.raises((ValueError, RuntimeError)):
        async with session:
            pass
    assert session.process is None
    assert not lease.path.exists()


async def test_cancellation_stops_owned_child_before_releasing_lease(tmp_path: Path) -> None:
    lease = MachineLease(tmp_path / "lease")
    lease.acquire("scripted child lifecycle")
    session = ModelSession(tmp_path, lease=lease)
    session.process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        "import time; time.sleep(30)",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    proc = session.process
    task = asyncio.create_task(
        session.complete([ChatMessage(role="user", content="synthetic process test")])
    )
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert proc.returncode is not None
    assert session.process is None
    assert not lease.path.exists()


@pytest.mark.parametrize("failure", ["metadata", "process"])
def test_failed_acquisition_leaves_no_owned_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    import psutil

    lease = MachineLease(tmp_path / "lease")
    if failure == "metadata":

        def fail_dump(*args: object, **kwargs: object) -> None:
            raise OSError("injected metadata failure")

        monkeypatch.setattr(json, "dump", fail_dump)
    else:

        def fail_process(_self: psutil.Process) -> float:
            raise psutil.AccessDenied()

        monkeypatch.setattr(psutil.Process, "create_time", fail_process)
    with pytest.raises((OSError, psutil.AccessDenied)):
        lease.acquire("scripted acquisition failure")
    assert not lease.owned
    assert not lease.path.exists()
