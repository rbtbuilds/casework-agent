import argparse
import importlib
import json
import sys
import time
from typing import Protocol, cast

from .contracts import JsonDict, StrictModel
from .model_adapter import ChatMessage


class Tokenizer(Protocol):
    def apply_chat_template(
        self, messages: list[dict[str, str]], *, tokenize: bool, add_generation_prompt: bool
    ) -> str: ...
    def encode(self, text: str) -> list[int]: ...


class MLX(Protocol):
    def load(self, path: str) -> tuple[object, Tokenizer]: ...
    def generate(
        self,
        model: object,
        tokenizer: Tokenizer,
        *,
        prompt: str,
        max_tokens: int,
        sampler: object,
        verbose: bool,
        logits_processors: list[object] | None,
    ) -> str: ...


class Samplers(Protocol):
    def make_sampler(self, *, temp: float) -> object: ...


class StructuredModule(Protocol):
    def from_mlxlm(self, model: object, tokenizer: Tokenizer) -> object: ...


class BackendModule(Protocol):
    def get_json_schema_logits_processor(
        self,
        backend_name: str,
        model: object,
        json_schema: str,
        whitespace_pattern: str | None = None,
    ) -> object: ...


class InferenceRequest(StrictModel):
    messages: list[ChatMessage]
    response_schema: JsonDict | None = None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    module = cast(MLX, importlib.import_module("mlx_lm"))
    samplers = cast(Samplers, importlib.import_module("mlx_lm.sample_utils"))
    model, tokenizer = module.load(args.snapshot)
    outlines = cast(StructuredModule, importlib.import_module("outlines"))
    backends = cast(BackendModule, importlib.import_module("outlines.backends"))
    structured = outlines.from_mlxlm(model, tokenizer)
    print(json.dumps({"status": "ready"}), flush=True)
    for line in sys.stdin:
        try:
            request = InferenceRequest.model_validate_json(line)
            messages = list(request.messages)
            processor: object | None = None
            if request.response_schema is not None:
                schema = json.dumps(request.response_schema, separators=(",", ":"))
                processor = backends.get_json_schema_logits_processor(
                    "outlines_core", structured, schema, whitespace_pattern=r"[ ]?"
                )
                messages.append(ChatMessage(role="user", content="NEXT_RESPONSE_SCHEMA=" + schema))
            prompt = tokenizer.apply_chat_template(
                [{"role": m.role, "content": m.content} for m in messages],
                tokenize=False,
                add_generation_prompt=True,
            )
            inputs = len(tokenizer.encode(prompt))
            if inputs > 8192:
                raise ValueError("prompt_tokens_limit")
            start = time.monotonic()
            text = module.generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=768,
                sampler=samplers.make_sampler(temp=0.0),
                verbose=False,
                logits_processors=[processor] if processor is not None else None,
            )
            print(
                json.dumps(
                    {
                        "text": text,
                        "input_tokens": inputs,
                        "output_tokens": len(tokenizer.encode(text)),
                        "elapsed_ms": (time.monotonic() - start) * 1000,
                    }
                ),
                flush=True,
            )
        except (ValueError, RuntimeError, OSError, TypeError, KeyError) as exc:
            print(json.dumps({"error": type(exc).__name__ + ": " + str(exc)[:200]}), flush=True)


if __name__ == "__main__":
    main()
