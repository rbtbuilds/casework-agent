import copy
import json
from pathlib import Path

from eval.contracts import EvaluationReport


def test_public_export_preserves_results_and_source_but_omits_host_metadata(tmp_path: Path) -> None:
    from eval.export_report import export_report

    original = Path('docs/evidence/qwen-full.json').read_bytes()
    raw = tmp_path / 'raw.json'
    raw.write_bytes(original)
    before = EvaluationReport.model_validate_json(original)
    target = tmp_path / 'public.json'
    export_report(raw, target)
    after = EvaluationReport.model_validate_json(target.read_text())
    assert raw.read_bytes() == original
    assert before.results == after.results
    assert before.score == after.score
    assert before.gates == after.gates
    assert 'runtime_root' not in after.provenance
    snapshot = after.provenance['snapshot']
    assert isinstance(snapshot, dict) and 'path' not in snapshot
    assert 'lease_owner' not in after.provenance
    assert '/Users/' not in target.read_text()
    assert after.provenance['publication_export']
    metadata = copy.deepcopy(json.loads(target.read_text())['provenance'])
    assert 'source_report_sha256' in metadata['publication_export']


def test_public_export_drops_external_manifest_path(tmp_path: Path) -> None:
    from eval.export_report import export_report

    value = json.loads(Path('docs/evidence/qwen-full.json').read_text())
    value['provenance']['manifest'] = '/Users/private-owner/private-directory/challenge.json'
    source, destination = tmp_path / 'raw.json', tmp_path / 'public.json'
    source.write_text(json.dumps(value))
    export_report(source, destination)
    assert '/Users/' not in destination.read_text()
    exported = json.loads(destination.read_text())
    assert 'provenance.manifest' in exported['provenance']['publication_export']['redacted_fields']
