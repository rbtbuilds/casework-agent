import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import model_session as cli


def test_prepare_pins_candidate_and_keeps_the_baseline_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    revisions: list[tuple[str, str]] = []

    class FakeApi:
        def __init__(self, *, token: bool) -> None:
            assert token is False

        def model_info(self, repo_id: str, *, revision: str) -> SimpleNamespace:
            revisions.append((repo_id, revision))
            return SimpleNamespace(sha=revision)

    class FakeDownloads:
        def snapshot_download(self, repo_id: str, **kwargs: object) -> str:
            patterns = kwargs["allow_patterns"]
            assert isinstance(patterns, list) and "*.jinja" in patterns
            target = kwargs["local_dir"]
            assert isinstance(target, Path)
            target.mkdir(parents=True, exist_ok=True)
            (target / "config.json").write_text("{}")
            return str(target)

    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "HfApi", FakeApi)

    def fake_import(_name: str) -> FakeDownloads:
        return FakeDownloads()

    monkeypatch.setattr(cli.importlib, "import_module", fake_import)
    cli.prepare("qwen7b")
    first = json.loads((tmp_path / ".runtime/models/snapshot.json").read_text())
    assert first["model_id"] == "mlx-community/Qwen2.5-7B-Instruct-4bit"
    assert first["revision"] == "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed"
    cli.prepare()
    selected = json.loads((tmp_path / ".runtime/models/snapshot.json").read_text())
    assert selected["model_id"] == "mlx-community/Qwen3-4B-Instruct-2507-4bit"
    assert selected["revision"] == "50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b"
    cli.prepare("baseline1.5b")
    second = json.loads((tmp_path / ".runtime/models/snapshot.json").read_text())
    assert second["model_id"] == "Qwen/Qwen2.5-1.5B-Instruct"
    assert second["revision"] == "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
    assert len(revisions) == 3
    assert Path(first["path"]).is_dir()


async def test_probe_certifies_loaded_snapshot_even_if_pointer_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from typing import Self

    from casework_agent.contracts import JsonDict
    from casework_agent.model_adapter import ChatMessage, ModelReply
    from casework_agent.model_session import Snapshot, snapshot_hash

    models = tmp_path / ".runtime/models"
    models.mkdir(parents=True)
    loaded = Snapshot(model_id="synthetic/A", revision="A", path=str(models), files={})
    changed = Snapshot(model_id="synthetic/B", revision="B", path=str(models), files={})

    class FakeSession:
        loaded_snapshot = loaded

        def __init__(self, root: Path, purpose: str) -> None:
            pass

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def complete(
            self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
        ) -> ModelReply:
            (models / "snapshot.json").write_text(changed.model_dump_json())
            return ModelReply(text='{"kind":"tool","name":"get_policy","arguments":{}}')

    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "ModelSession", FakeSession)
    await cli.probe()
    result = json.loads((tmp_path / ".runtime/model-probe.json").read_text())
    assert result["snapshot_hash"] == snapshot_hash(loaded)
    assert result["snapshot_hash"] != snapshot_hash(changed)
