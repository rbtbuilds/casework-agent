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

from casework_agent.contracts import JsonDict
from casework_agent.model_adapter import MODEL_PROTOCOL_VERSION, REQUEST, ChatMessage
from casework_agent.model_session import ModelSession, snapshot_hash
from eval.runner import evaluate

ROOT = Path(__file__).resolve().parents[1]
MODEL_PROFILES = {
    "qwen3-14b": (
        "mlx-community/Qwen3-14B-4bit",
        "a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4",
    ),
    "qwen3-4b": (
        "mlx-community/Qwen3-4B-Instruct-2507-4bit",
        "50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b",
    ),
    "qwen7b": (
        "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
    ),
    "baseline1.5b": (
        "Qwen/Qwen2.5-1.5B-Instruct",
        "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    ),
}


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


def prepare(profile: str = "qwen3-14b") -> None:
    model_id, revision = MODEL_PROFILES[profile]
    info = HfApi(token=False).model_info(model_id, revision=revision)
    if info.sha != revision:
        raise RuntimeError("No immutable revision")
    target = ROOT / ".runtime/models" / model_id.split("/")[-1].lower() / revision
    cast(HubDownloads, importlib.import_module("huggingface_hub")).snapshot_download(
        model_id,
        revision=revision,
        token=False,
        local_dir=target,
        cache_dir=ROOT / ".runtime/hf-cache",
        max_workers=2,
        allow_patterns=[
            "*.safetensors",
            "*.json",
            "*.txt",
            "*.model",
            "*.jinja",
            "LICENSE",
            "README.md",
        ],
    )
    files: dict[str, str] = {}
    for path in sorted(target.iterdir()):
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            files[path.name] = digest.hexdigest()
    pointer = ROOT / ".runtime/models/snapshot.json"
    temporary = pointer.with_suffix(".pending.json")
    temporary.write_text(
        json.dumps(
            {"model_id": model_id, "revision": revision, "path": str(target), "files": files},
            indent=2,
        )
    )
    temporary.replace(pointer)
    print(json.dumps({"model_id": model_id, "revision": revision, "file_count": len(files)}))


async def probe() -> None:
    async with ModelSession(ROOT, "casework compatibility probe") as session:
        reply = await session.complete(
            [
                ChatMessage(
                    role="system",
                    content='Return exactly {"kind":"tool","name":"get_policy","arguments":{}} without markdown.',
                ),
                ChatMessage(role="user", content="Read the policy."),
            ],
            response_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "kind": {"const": "tool"},
                    "name": {"const": "get_policy"},
                    "arguments": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
                "required": ["kind", "name", "arguments"],
            },
        )
        valid = True
        try:
            REQUEST.validate_json(reply.text)
        except ValidationError:
            valid = False
        assert session.loaded_snapshot is not None
        result = {
            "protocol_valid": valid,
            "protocol_version": MODEL_PROTOCOL_VERSION,
            "snapshot_hash": snapshot_hash(session.loaded_snapshot),
            "reply": reply.model_dump(mode="json"),
        }
        (ROOT / ".runtime/model-probe.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result))


async def benchmark(manifest: Path, output: Path) -> None:
    started = time.monotonic()
    async with ModelSession(ROOT, "casework model evaluation") as session:
        load_ms = (time.monotonic() - started) * 1000
        report = await evaluate(manifest.resolve(), "model", output.resolve(), session)
        assert session.loaded_snapshot is not None
        report.provenance["snapshot"] = cast(
            JsonDict, session.loaded_snapshot.model_dump(mode="json")
        )
        report.provenance.update(
            {
                "load_ms": load_ms,
                "mlx_lm": importlib.metadata.version("mlx-lm"),
                "mlx": importlib.metadata.version("mlx"),
                "outlines": importlib.metadata.version("outlines"),
                "decoder": "outlines_core JSON Schema",
                "enable_thinking": False,
                "prompt_rendering": "merged consecutive turns; schema appended to final user turn",
                "protocol_version": MODEL_PROTOCOL_VERSION,
                "lease_owner": json.loads((session.lease.path / "owner.json").read_text()),
                "worker_protocol": "typed JSON lines on owned subprocess pipes",
            }
        )
    report.provenance["worker_exited_before_lease_release"] = True
    output.write_text(report.model_dump_json(indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "probe", "evaluate"])
    parser.add_argument("--profile", choices=list(MODEL_PROFILES), default="qwen3-14b")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.profile)
    elif args.command == "probe":
        asyncio.run(probe())
    else:
        if not args.manifest or not args.output:
            parser.error("evaluate requires --manifest and --output")
        asyncio.run(benchmark(args.manifest, args.output))
