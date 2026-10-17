import json
from pathlib import Path

import pytest

from eval.contracts import EvaluationReport, Manifest
from scripts.audit_retained_v5 import audit_case, capture_case


def test_retained_capture_is_optional_for_portable_audit() -> None:
    from scripts.audit_retained_v5 import audit_report

    root = Path(__file__).resolve().parents[2]
    report = root / "docs/evidence/qwen-v5-challenge.json"
    manifest = root / "fixtures/manifests/v5-challenge.json"
    result = audit_report(report, manifest, None)
    assert result["issues"] == []
    assert result["remote_effect_verification"] == "not_available"
    assert result["human_review"] == "pending"


@pytest.mark.parametrize("mutation", ["observation", "hash", "human_gate", "effect_count"])
def test_retained_audit_rejects_inconsistent_report(mutation: str) -> None:
    from scripts.audit_retained_v5 import audit_report_data

    root = Path(__file__).resolve().parents[2]
    report = EvaluationReport.model_validate_json(
        (root / "docs/evidence/qwen-v5-challenge.json").read_text()
    )
    manifest = Manifest.model_validate_json(
        (root / "fixtures/manifests/v5-challenge.json").read_text()
    )
    row = report.results[0]
    if mutation == "observation":
        exchange = row.trace["exchange"]
        assert isinstance(exchange, list)
        message = exchange[3]
        assert isinstance(message, dict)
        observation = json.loads(str(message["content"]).split("=", 1)[1])
        observation["payload"]["status"] = "delivered"
        message["content"] = "UNTRUSTED_OBSERVATION=" + json.dumps(observation)
    elif mutation == "hash":
        assert row.proposal
        row.proposal["hash"] = "0" * 64
    elif mutation == "human_gate":
        report.gates["claims_review"] = True
    else:
        row.tickets = 1
    assert audit_report_data(report, manifest, root, None)["issues"]


def test_capture_refuses_missing_databases_without_creating_files(tmp_path: Path) -> None:
    # Capture uses read-only SQLite; it must not create missing databases.
    with pytest.raises(FileNotFoundError):
        capture_case(tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("mutation", ["journal", "approval", "request", "extra_effect", "order"])
def test_remote_binding_rejects_modified_journal_and_approval(mutation: str) -> None:
    root = Path(__file__).resolve().parents[2]
    report = EvaluationReport.model_validate_json(
        (root / "docs/evidence/qwen-v5-challenge.json").read_text()
    )
    manifest = Manifest.model_validate_json(
        (root / "fixtures/manifests/v5-challenge.json").read_text()
    )
    snapshots = json.loads(
        (root / "docs/evidence/v5-retained-database-export-2026-10-17.json").read_text()
    )
    result = next(r for r in report.results if r.approved)
    scenario = json.loads(
        (
            root / next(r.scenario_file for r in manifest.cases if r.case_id == result.case_id)
        ).read_text()
    )
    snapshot = snapshots[result.case_id]
    assert audit_case(result, scenario, snapshot) == []
    if mutation == "extra_effect":
        snapshot["tickets"]["tickets"].append(snapshot["tickets"]["tickets"][0])
    elif mutation == "order":
        row = snapshot["orders"]["orders"][0]
        payload = json.loads(row["payload"])
        payload["version"] += 1
        row["payload"] = json.dumps(payload)
    else:
        table, column = (
            {
                "journal": ("idempotency", "payload"),
                "approval": ("approvals", "payload_json"),
                "request": ("operations", "payload_json"),
            }
        )[mutation]
        row = snapshot["tickets" if mutation == "journal" else "app"][table][0]
        payload = json.loads(row[column])
        if mutation == "request":
            payload["request_json"]["internal_note"] = "An unapproved replacement note."
        else:
            payload["request_hash" if mutation == "journal" else "proposal_hash"] = "0" * 64
        row[column] = json.dumps(payload)
    assert audit_case(result, scenario, snapshot)
