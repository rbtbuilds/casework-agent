import argparse
import asyncio
import hashlib
import importlib
import importlib.metadata
import json
import time
from pathlib import Path
from typing import Protocol, cast

from huggingface_hub import HfApi
from pydantic import ValidationError

from casework_agent.model_adapter import REQUEST, ChatMessage
from casework_agent.model_session import ModelSession
from eval.runner import evaluate

ROOT = Path(__file__).resolve().parents[1]
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


class HubDownloads(Protocol):
    def snapshot_download(
        self,
        repo_id: str,
        *,
        revision: str,
        token: bool,
        local_dir: Path,
        cache_dir: Path,
        max_workers: int,
        allow_patterns: list[str],
    ) -> str: ...


def prepare() -> None:
    info = HfApi(token=False).model_info(MODEL)
    if not info.sha:
        raise RuntimeError("No immutable revision")
    target = ROOT / ".runtime/models/qwen2.5-1.5b-instruct" / info.sha
    cast(HubDownloads, importlib.import_module("huggingface_hub")).snapshot_download(
        MODEL,
        revision=info.sha,
        token=False,
        local_dir=target,
        cache_dir=ROOT / ".runtime/hf-cache",
        max_workers=2,
        allow_patterns=["*.safetensors", "*.json", "*.txt", "*.model", "LICENSE", "README.md"],
    )
    files: dict[str, str] = {}
    for path in sorted(target.iterdir()):
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            files[path.name] = digest.hexdigest()
    (ROOT / ".runtime/models/snapshot.json").write_text(
        json.dumps(
            {"model_id": MODEL, "revision": info.sha, "path": str(target), "files": files}, indent=2
        )
    )
    print(json.dumps({"revision": info.sha, "file_count": len(files)}))


async def probe() -> None:
    async with ModelSession(ROOT, "casework compatibility probe") as session:
        reply = await session.complete(
            [
                ChatMessage(
                    role="system",
                    content='Return exactly {"kind":"tool","name":"get_policy","arguments":{}} without markdown.',
                ),
                ChatMessage(role="user", content="Read the policy."),
            ]
        )
        valid = True
        try:
            REQUEST.validate_json(reply.text)
        except ValidationError:
            valid = False
        result = {"protocol_valid": valid, "reply": reply.model_dump(mode="json")}
        (ROOT / ".runtime/model-probe.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result))


async def benchmark(manifest: Path, output: Path) -> None:
    started = time.monotonic()
    async with ModelSession(ROOT, "casework held-out evaluation") as session:
        load_ms = (time.monotonic() - started) * 1000
        report = await evaluate(manifest.resolve(), "model", output.resolve(), session)
        report.provenance.update(
            {
                "load_ms": load_ms,
                "mlx_lm": importlib.metadata.version("mlx-lm"),
                "mlx": importlib.metadata.version("mlx"),
                "lease_owner": json.loads((session.lease.path / "owner.json").read_text()),
                "worker_protocol": "typed JSON lines on owned subprocess pipes",
            }
        )
    report.provenance["worker_exited_before_lease_release"] = True
    output.write_text(report.model_dump_json(indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "probe", "evaluate"])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "probe":
        asyncio.run(probe())
    else:
        if not args.manifest or not args.output:
            parser.error("evaluate requires --manifest and --output")
        asyncio.run(benchmark(args.manifest, args.output))
