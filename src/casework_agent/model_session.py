import asyncio
import hashlib
import json
import os
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Self, cast

import psutil
from pydantic import BaseModel

from .contracts import JsonDict
from .hashing import canonical_hash
from .model_adapter import MODEL_PROTOCOL_VERSION, ChatMessage, ModelReply


class ModelBusy(RuntimeError):
    pass


class ModelUnavailable(RuntimeError):
    pass


class MachineLease:
    def __init__(self, path: Path = Path("/tmp/bentolabs-portfolio-ml.lock")) -> None:
        self.path = path
        self.token = secrets.token_hex(16)
        self.owned = False

    def acquire(self, purpose: str) -> None:
        info = {
            "project": "casework-agent",
            "pid": os.getpid(),
            "process_start": psutil.Process().create_time(),
            "started_at": datetime.now(UTC).isoformat(),
            "purpose": purpose,
            "owner_token": self.token,
        }
        try:
            self.path.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise ModelBusy("model_busy") from exc
        directory = self.path.stat()
        owner_path = self.path / "owner.json"
        owner_identity: tuple[int, int] | None = None
        try:
            with owner_path.open("x") as stream:
                identity = os.fstat(stream.fileno())
                owner_identity = (identity.st_dev, identity.st_ino)
                json.dump(info, stream)
        except BaseException:
            # Never remove a replaced directory or a metadata file we did not create.
            current = self.path.stat()
            if (current.st_dev, current.st_ino) == (directory.st_dev, directory.st_ino):
                if owner_identity is not None and owner_path.exists():
                    current_owner = owner_path.stat()
                    if (current_owner.st_dev, current_owner.st_ino) == owner_identity:
                        owner_path.unlink()
                try:
                    self.path.rmdir()
                except OSError:
                    pass
            raise
        self.owned = True

    def release(self) -> None:
        if not self.owned:
            return
        owner = json.loads((self.path / "owner.json").read_text())
        if owner.get("owner_token") != self.token:
            raise RuntimeError("lease_owner_changed")
        (self.path / "owner.json").unlink()
        self.path.rmdir()
        self.owned = False


class Snapshot(BaseModel):
    revision: str
    path: str
    files: dict[str, str]
    model_id: str = "Qwen/Qwen2.5-1.5B-Instruct"


def snapshot(root: Path) -> Snapshot:
    pointer = root / ".runtime/models/snapshot.json"
    if not pointer.exists():
        raise ModelUnavailable("model_missing: run model_session.py prepare")
    value = Snapshot.model_validate_json(pointer.read_text())
    base = Path(value.path).resolve()
    if not base.is_relative_to((root / ".runtime/models").resolve()):
        raise ModelUnavailable("snapshot_path_outside_runtime")
    return value


def snapshot_hash(value: Snapshot) -> str:
    return canonical_hash(
        {"model_id": value.model_id, "revision": value.revision, "files": value.files}
    )


def model_ready(root: Path) -> bool:
    try:
        value = snapshot(root)
        probe = json.loads((root / ".runtime/model-probe.json").read_text())
        return (
            probe.get("protocol_valid") is True
            and probe.get("protocol_version") == MODEL_PROTOCOL_VERSION
            and probe.get("snapshot_hash") == snapshot_hash(value)
        )
    except (RuntimeError, OSError, ValueError, AttributeError):
        return False


class ModelSession:
    def __init__(
        self, root: Path, purpose: str = "casework model", lease: MachineLease | None = None
    ) -> None:
        self.root = root
        self.purpose = purpose
        self.lease = lease or MachineLease()
        self.process: asyncio.subprocess.Process | None = None
        self.loaded_snapshot: Snapshot | None = None
        self.log_path = root / ".runtime/model-worker.log"

    async def __aenter__(self) -> Self:
        value = snapshot(self.root)
        self.loaded_snapshot = value
        self.lease.acquire(self.purpose)
        try:
            for name, want in value.files.items():
                path = Path(value.path) / name
                if not path.is_file() or not path.resolve().is_relative_to(
                    Path(value.path).resolve()
                ):
                    raise ModelUnavailable("snapshot_file_invalid")
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                if digest.hexdigest() != want:
                    raise ModelUnavailable("snapshot_hash_mismatch")
            with self.log_path.open("ab") as log:
                self.process = await asyncio.create_subprocess_exec(
                    sys.executable,
                    "-m",
                    "casework_agent.model_worker",
                    "--snapshot",
                    value.path,
                    cwd=self.root,
                    env=dict(
                        os.environ,
                        OUTLINES_CACHE_DIR=str(self.root / ".runtime/outlines-cache"),
                        HF_HUB_OFFLINE="1",
                        TRANSFORMERS_OFFLINE="1",
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=log,
                    limit=65536,
                )
            assert self.process.stdout is not None
            line = await asyncio.wait_for(self.process.stdout.readline(), timeout=120)
            if not line or json.loads(line).get("status") != "ready":
                raise ModelUnavailable("model_start_failed: inspect .runtime/model-worker.log")
            return self
        except BaseException:
            await self.close()
            raise

    async def complete(
        self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
    ) -> ModelReply:
        proc = self.process
        if proc is None or proc.stdin is None or proc.stdout is None:
            raise ModelUnavailable("worker_not_running")
        raw = (
            json.dumps(
                {"messages": [m.model_dump() for m in messages], "response_schema": response_schema}
            ).encode()
            + b"\n"
        )
        if len(raw) > 32768:
            raise ModelUnavailable("prompt_bytes_limit")
        proc.stdin.write(raw)
        await proc.stdin.drain()
        try:
            line = await asyncio.wait_for(proc.stdout.readline(), timeout=120)
        except BaseException:
            await self.close()
            raise
        if not line or len(line) > 32768:
            raise ModelUnavailable("worker_reply_limit")
        data = cast(JsonDict, json.loads(line))
        if "error" in data:
            raise ModelUnavailable(str(data["error"]))
        return ModelReply.model_validate(data)

    async def close(self) -> None:
        proc = self.process
        if proc is not None:
            if proc.stdin:
                proc.stdin.close()
            if proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=5)
                except TimeoutError:
                    proc.kill()
                    await proc.wait()
            self.process = None
        self.lease.release()

    async def __aexit__(self, *args: object) -> None:
        await self.close()
