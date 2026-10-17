"""Recheck retained v5 observations and optional read-only database exports.

This supplements the frozen independent trace/oracle auditors. It does not
rerun inference, infer human review, or establish historical database authenticity.
"""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, cast

from casework_agent.contracts import Order, Proposal, Shipment
from casework_agent.hashing import canonical_hash
from eval.contracts import CaseResult, EvaluationReport, Manifest

type Record = dict[str, Any]


def capture_case(root: Path) -> Record:
    paths = {
        "app": root / ".runtime/app.sqlite3",
        "orders": root / "orders.sqlite3",
        "carrier": root / "carrier.sqlite3",
        "tickets": root / "tickets.sqlite3",
    }
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path.name)
    snapshot: Record = {"database_sha256": {}}
    tables = {
        "app": ["cases", "evidence", "proposals", "approvals", "operations", "audit_events"],
        "orders": ["orders", "annotations", "idempotency"],
        "carrier": ["shipments"],
        "tickets": ["tickets", "idempotency"],
    }
    for name, path in paths.items():
        snapshot["database_sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as con:
            con.row_factory = sqlite3.Row
            snapshot[name] = {
                table: [dict(row) for row in con.execute(f'SELECT * FROM "{table}"')]
                for table in tables[name]
            }
    return snapshot


def audit_case(result: CaseResult, scenario: Record, snapshot: Record | None) -> list[str]:
    issues: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            issues.append(label)

    messages = cast(list[Record], result.trace.get("exchange", []))
    observations: list[Record] = [
        json.loads(str(m["content"]).removeprefix("UNTRUSTED_OBSERVATION="))
        for m in messages
        if str(m.get("content", "")).startswith("UNTRUSTED_OBSERVATION=")
    ]
    by_source = {o["source"]: o for o in observations}
    check(
        len(observations) == 3 and set(by_source) == {"order", "carrier", "policy"},
        "observation_coverage",
    )
    expected = {
        "order": Order.model_validate(scenario["order"]).model_dump(mode="json"),
        "carrier": Shipment.model_validate(scenario["shipment"]).model_dump(mode="json"),
    }
    for source, payload in expected.items():
        check(by_source.get(source, {}).get("payload") == payload, f"{source}_source_payload")
    policy = json.loads(str(messages[0]["content"]).split("Policy: ", 1)[1])
    check(by_source.get("policy", {}).get("payload") == policy, "policy_source_payload")
    for observation in observations:
        check(
            canonical_hash(observation["payload"]) == observation["payload_hash"],
            "observation_payload_hash",
        )
    proposal = Proposal.model_validate(result.proposal)
    check(
        proposal.hash == canonical_hash(proposal.model_dump(mode="json", exclude={"hash"})),
        "proposal_hash",
    )
    check(
        proposal.evidence_hashes == [o["payload_hash"] for o in observations],
        "proposal_evidence_hashes",
    )
    check(proposal.evidence_ids == [o["id"] for o in observations], "proposal_evidence_ids")
    check(proposal.policy_hash == by_source.get("policy", {}).get("payload_hash"), "policy_hash")
    check(
        (result.tickets, result.annotations)
        == (result.expected_tickets, result.expected_annotations),
        "reported_effect_counts",
    )
    check(result.approved or (result.tickets == result.annotations == 0), "unapproved_effect")
    check(result.unsupported_claims is None, "human_review_not_pending")
    if snapshot is None:
        return issues
    app = snapshot["app"]
    check(len(app["cases"]) == 1, "database_case_coverage")
    saved = app["cases"][0]
    check(
        saved["id"] == proposal.case_id and saved["state"] == result.final_state,
        "database_case_binding",
    )
    check(json.loads(saved["seed_json"])["scenario_id"] == result.case_id, "database_scenario")
    check(
        [json.loads(p["payload_json"]) for p in app["proposals"]] == [result.proposal],
        "database_proposal",
    )
    check(
        {e["id"]: json.loads(e["payload_json"]) for e in app["evidence"]}
        == {o["id"]: o for o in observations},
        "database_observations",
    )
    approvals: list[Record] = [json.loads(a["payload_json"]) for a in app["approvals"]]
    operations: list[Record] = sorted(
        [json.loads(o["payload_json"]) for o in app["operations"]], key=lambda o: o["ordinal"]
    )
    ticket_rows = snapshot["tickets"]["tickets"]
    annotation_rows = snapshot["orders"]["annotations"]
    check(
        (len(ticket_rows), len(annotation_rows)) == (result.tickets, result.annotations),
        "database_effect_counts",
    )
    if not result.approved:
        check(not approvals and not operations, "stale_authority")
        check(
            not snapshot["tickets"]["idempotency"] and not snapshot["orders"]["idempotency"],
            "stale_remote_journals",
        )
        return issues
    check(len(approvals) == 1 and len(operations) == 2, "approved_operation_coverage")
    if len(approvals) != 1 or len(operations) != 2 or not ticket_rows or not annotation_rows:
        return issues
    approval = approvals[0]
    check(
        approval["proposal_id"] == proposal.id
        and approval["proposal_hash"] == proposal.hash
        and approval["decision"] == "approve"
        and approval["case_id"] == proposal.case_id,
        "exact_approval_binding",
    )
    ticket: Record = json.loads(ticket_rows[0]["payload"])
    annotation: Record = json.loads(annotation_rows[0]["payload"])
    first, second = proposal.model_dump(mode="json")["intents"]
    expected_requests = [
        {k: v for k, v in first.items() if k != "kind"},
        {k: v for k, v in second.items() if k not in {"kind", "ticket_ref"}}
        | {"ticket_id": ticket["ticket_id"]},
    ]
    for index, (op, service, effect, remote_id) in enumerate(
        zip(
            operations,
            ["tickets", "orders"],
            [ticket, annotation],
            [ticket["ticket_id"], annotation["annotation_id"]],
            strict=True,
        )
    ):
        expected_key = f"cw:{proposal.case_id}:{proposal.version}:" + (
            "ticket" if index == 0 else "annotation"
        )
        check(op["key"] == expected_key == effect["operation_key"], "operation_key")
        check(
            op["approval_id"] == approval["id"] and op["case_id"] == proposal.case_id,
            "operation_authority",
        )
        check(op["request_json"] == expected_requests[index], "approved_request_body")
        check(op["request_hash"] == canonical_hash(op["request_json"]), "operation_body_hash")
        check(
            op["state"] == "succeeded"
            and op["attempts"] == 1
            and op["remote_id"] == remote_id
            and op["response_json"] == effect,
            "confirmed_operation_effect",
        )
        journals = snapshot[service]["idempotency"]
        check(len(journals) == 1, "remote_journal_coverage")
        if len(journals) == 1:
            journal = json.loads(journals[0]["payload"])
            check(
                journals[0]["key"] == journal["key"] == op["key"]
                and journals[0]["request_hash"] == journal["request_hash"] == op["request_hash"]
                and journal["outcome"] == "succeeded"
                and journal["http_status"] == 201
                and journal["response_json"] == effect,
                "remote_journal_binding",
            )
    check({k: ticket[k] for k in expected_requests[0]} == expected_requests[0], "ticket_payload")
    check(
        annotation["ticket_id"] == ticket["ticket_id"] and annotation["action"] == proposal.action,
        "annotation_ticket_binding",
    )
    final_order = json.loads(snapshot["orders"]["orders"][0]["payload"])
    check(
        final_order["version"] == proposal.order_version + 1
        and final_order["annotations"] == [annotation],
        "final_order_effect",
    )
    events = app["audit_events"]
    approval_events = [e for e in events if e["kind"] == "approved"]
    claims = [e for e in events if e["kind"] == "operation_claimed"]
    check(
        len(approval_events) == 1
        and len(claims) == 2
        and all(e["id"] > approval_events[0]["id"] for e in claims),
        "approval_before_claims",
    )
    return issues


def audit_report_data(
    report: EvaluationReport, manifest: Manifest, root: Path, snapshots: Record | None
) -> Record:
    issues: list[str] = []
    if report.gates["claims_review"] is not False or report.score.claims_review_complete:
        issues.append("human_gate_not_pending")
    if report.score.unsupported_claims is not None:
        issues.append("human_claim_count_not_pending")
    rows = {r.case_id: r for r in manifest.cases}
    if len(rows) != len(report.results) or set(rows) != {r.case_id for r in report.results}:
        issues.append("report_case_coverage")
    if snapshots is not None and set(snapshots) != set(rows):
        issues.append("snapshot_case_coverage")
    cases: list[Record] = []
    for result in report.results:
        scenario_path = (root / rows[result.case_id].scenario_file).resolve()
        if not scenario_path.is_relative_to((root / "fixtures/scenarios").resolve()):
            raise ValueError("Scenario outside fixtures")
        scenario = json.loads(scenario_path.read_text())
        if (
            hashlib.sha256(scenario_path.read_bytes()).hexdigest()
            != rows[result.case_id].scenario_hash
        ):
            issues.append(f"{result.case_id}:scenario_hash")
        found = audit_case(result, scenario, snapshots[result.case_id] if snapshots else None)
        issues.extend(f"{result.case_id}:{issue}" for issue in found)
        cases.append(
            {
                "case_id": result.case_id,
                "issues": found,
                "approved": result.approved,
                "tickets": result.tickets,
                "annotations": result.annotations,
            }
        )
    return {
        "kind": "deterministic retained-evidence audit; not human review",
        "human_review": "pending",
        "remote_effect_verification": "retained_database_exports"
        if snapshots is not None
        else "not_available",
        "issues": issues,
        "cases": cases,
    }


def audit_report(report_path: Path, manifest_path: Path, snapshots: Record | None) -> Record:
    root = Path(__file__).resolve().parents[1]
    report = EvaluationReport.model_validate_json(report_path.read_text())
    manifest = Manifest.model_validate_json(manifest_path.read_text())
    result = audit_report_data(report, manifest, root, snapshots)
    result["input_sha256"] = {
        "report": hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "manifest": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "auditor": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--snapshots", type=Path, required=True)
    parser.add_argument("--capture-runtime", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.capture_runtime:
        report = EvaluationReport.model_validate_json(args.report.read_text())
        snapshots = {
            r.case_id: capture_case(args.capture_runtime / r.case_id) for r in report.results
        }
        with args.snapshots.open("x") as file:
            file.write(json.dumps(snapshots, indent=2) + "\n")
    snapshots = json.loads(args.snapshots.read_text())
    result = audit_report(args.report, args.manifest, snapshots)
    result["input_sha256"]["snapshots"] = hashlib.sha256(args.snapshots.read_bytes()).hexdigest()
    with args.output.open("x") as file:
        file.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"cases": len(result["cases"]), "issues": result["issues"]}))
    if result["issues"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
