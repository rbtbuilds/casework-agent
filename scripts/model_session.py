import argparse
import asyncio
import hashlib
import importlib
import json
from pathlib import Path
from typing import Protocol, cast

from huggingface_hub import HfApi

from casework_agent.model_adapter import ChatMessage
from casework_agent.model_session import ModelSession

ROOT=Path(__file__).resolve().parents[1]
MODEL="Qwen/Qwen2.5-1.5B-Instruct"

class HubDownloads(Protocol):
    def snapshot_download(self, repo_id: str, *, revision: str, token: bool, local_dir: Path, cache_dir: Path, max_workers: int, allow_patterns: list[str]) -> str: ...


def prepare() -> None:
    info=HfApi(token=False).model_info(MODEL)
    if not info.sha:raise RuntimeError("No immutable revision")
    target=ROOT/".runtime/models/qwen2.5-1.5b-instruct"/info.sha
    cast(HubDownloads, importlib.import_module("huggingface_hub")).snapshot_download(MODEL,revision=info.sha,token=False,local_dir=target,cache_dir=ROOT/".runtime/hf-cache",max_workers=2,allow_patterns=["*.safetensors","*.json","*.txt","*.model","LICENSE","README.md"])
    files: dict[str,str]={}
    for path in sorted(target.iterdir()):
        if path.is_file():
            digest=hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda:stream.read(1024*1024),b""):digest.update(block)
            files[path.name]=digest.hexdigest()
    (ROOT/".runtime/models/snapshot.json").write_text(json.dumps({"model_id":MODEL,"revision":info.sha,"path":str(target),"files":files},indent=2))
    print(json.dumps({"revision":info.sha,"file_count":len(files)}))

async def probe() -> None:
    async with ModelSession(ROOT,"casework compatibility probe") as session:
        reply=await session.complete([ChatMessage(role="system",content='Return exactly {"kind":"tool","name":"get_policy","arguments":{}} without markdown.'),ChatMessage(role="user",content="Read the policy.")])
        print(reply.model_dump_json())

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=["prepare","probe"])
    args=parser.parse_args()
    if args.command=="prepare":prepare()
    else:asyncio.run(probe())
