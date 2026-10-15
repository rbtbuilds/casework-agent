import json
from pathlib import Path

from eval.contracts import Manifest
from eval.runner import evaluate

ROOT = Path(__file__).resolve().parents[2]


async def test_evaluation_records_a_real_http_fixture_case(tmp_path: Path) -> None:
    manifest = Manifest.model_validate_json((ROOT / "fixtures/manifests/holdout.json").read_text())
    manifest.cases = manifest.cases[:1]
    path = tmp_path / "manifest.json"
    path.write_text(manifest.model_dump_json())
    output = tmp_path / "report.json"
    report = await evaluate(path, "fixture", output)
    assert report.mode == "fixture"
    assert report.score.valid_action_count == 1
    assert report.score.authorized_completion_count == 1
    assert report.score.usage_tokens is None
    assert json.loads(output.read_text())["results"][0]["tickets"] == 1
