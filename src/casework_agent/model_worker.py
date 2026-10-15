import argparse
import importlib
import json
import sys
import time
from typing import Protocol, cast

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
    ) -> str: ...


class Samplers(Protocol):
    def make_sampler(self, *, temp: float) -> object: ...


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    module = cast(MLX, importlib.import_module("mlx_lm"))
    samplers = cast(Samplers, importlib.import_module("mlx_lm.sample_utils"))
    model, tokenizer = module.load(args.snapshot)
    print(json.dumps({"status": "ready"}), flush=True)
    for line in sys.stdin:
        try:
            data = json.loads(line)
            messages = [ChatMessage.model_validate(m) for m in data["messages"]]
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
