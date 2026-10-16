import argparse
import asyncio
import hashlib
import json
import platform
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal, cast

from casework_agent.clock import FrozenClock
from casework_agent.config import Settings
from casework_agent.contracts import ApprovalRequest, CaseSeed, JsonDict, uid
from casework_agent.grounded_explanation import EXPLANATION_VERSION
from casework_agent.hashing import canonical_hash
from casework_agent.model_adapter import (
    MODEL_PROTOCOL_VERSION,
    REQUEST,
    ModelClient,
    protocol_definition,
    system_instruction,
)
from casework_agent.repository import Conflict, Repository
from casework_agent.worker import Worker
from casework_agent.workflow import Workflow

from .contracts import CaseResult, EvaluationReport, Manifest, ManifestRow
from .model_claims import summarize_claims
from .scoring import strict_quality_gates, summarize
from .services import ROOT, Services


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def run_case(
    row: ManifestRow, mode: Literal["fixture", "model"], root: Path, model: ModelClient | None
) -> CaseResult:
    source = (ROOT / row.scenario_file).resolve()
    if (
        not source.is_relative_to(ROOT / "fixtures/scenarios")
        or digest(source) != row.scenario_hash
    ):
        raise ValueError("frozen_scenario_hash_mismatch")
    root.mkdir(parents=True)
    (root / "scenario.json").write_bytes(source.read_bytes())
    raw = cast(JsonDict, json.loads(source.read_text()))
    order = cast(JsonDict, raw["order"])
    seed = CaseSeed(
        scenario_id=row.case_id,
        order_id=str(order["order_id"]),
        as_of=datetime.fromisoformat(row.as_of),
        mode=mode,
    )
    async with Services(root, row.fault_checkpoint) as services:
        with Repository.open(root / ".runtime/app.sqlite3") as repo:
            flow = Workflow(repo, Settings(root=root, run_worker=False), model)
            case = repo.create_case(seed)
            start = time.monotonic()
            await flow.gather(case.id)
            gathered = repo.get_case(case.id)
            decision = gathered.proposal
            approved = False
            if decision:
                if row.fault_checkpoint == "expire":
                    repo.clock = FrozenClock(decision.expires_at + timedelta(seconds=1))
                elif row.fault_checkpoint in {"order_version", "carrier_version"}:
                    import sqlite3

                    service = "orders" if row.fault_checkpoint == "order_version" else "carrier"
                    table = "orders" if service == "orders" else "shipments"
                    await services.stop_one(service)
                    with sqlite3.connect(root / f"{service}.sqlite3") as con:
                        payload = json.loads(
                            con.execute(f"SELECT payload FROM {table}").fetchone()[0]
                        )
                        payload["version"] += 1
                        con.execute(f"UPDATE {table} SET payload=?", (json.dumps(payload),))
                    await services.spawn(service)
                body = ApprovalRequest(
                    proposal_id=decision.id,
                    proposal_hash=decision.hash,
                    expected_case_version=gathered.version,
                    decision="approve",
                )
                try:
                    first = await flow.decide(case.id, body, "scripted-exact-approval")
                    approved = True
                    if row.fault_checkpoint == "decision_replay":
                        assert await flow.decide(case.id, body, "scripted-exact-approval") == first
                except Conflict:
                    if row.expected_final_state != "stale":
                        raise
                worker = Worker(repo, flow.settings, model=model)
                try:
                    for _ in range(10):
                        await worker.tick()
                        if repo.get_case(case.id).state in {
                            "completed",
                            "stale",
                            "failed",
                            "review_required",
                        }:
                            break
                finally:
                    await worker.close()
            final = repo.get_case(case.id)
            tickets, annotations = services.counts()
            run = repo.con.execute(
                "SELECT payload_json FROM agent_runs WHERE case_id=? ORDER BY rowid DESC LIMIT 1",
                (case.id,),
            ).fetchone()
            trace = cast(JsonDict, json.loads(run[0])) if run else {}
            usage = trace.get("usage_tokens")
            calls = trace.get("tool_calls", len(gathered.evidence))
            return CaseResult(
                case_id=row.case_id,
                family=row.family,
                expected_action=row.expected_action,
                proposed_action=decision.action if decision else None,
                expected_final_state=row.expected_final_state,
                final_state=final.state,
                approved=approved,
                unapproved_writes=(tickets + annotations) if not approved else 0,
                duplicate_effects=max(tickets - 1, 0) + max(annotations - 1, 0),
                unsupported_claims=0 if mode == "fixture" else None,
                usage_tokens=usage if isinstance(usage, int) else None,
                elapsed_ms=(time.monotonic() - start) * 1000,
                tool_calls=calls if isinstance(calls, int) else 0,
                tickets=tickets,
                annotations=annotations,
                expected_tickets=row.expected_ticket_count,
                expected_annotations=row.expected_annotation_count,
                error=final.error.message if final.error else None,
                proposal=cast(JsonDict, decision.model_dump(mode="json")) if decision else None,
                trace=trace,
            )


async def evaluate(
    manifest: Path,
    mode: Literal["fixture", "model"],
    output: Path,
    model: ModelClient | None = None,
) -> EvaluationReport:
    if mode == "model" and model is None:
        raise ValueError(
            "Model evaluation requires an owned borrowed ModelSession; use scripts/model_session.py evaluate"
        )
    frozen = Manifest.model_validate_json(manifest.read_text())
    root = ROOT / ".runtime/eval" / uid()
    results: list[CaseResult] = []
    started = datetime.now(UTC)
    for row in frozen.cases:
        result = await run_case(row, mode, root / row.case_id, model)
        results.append(result)
        print(
            json.dumps(
                {"case": row.case_id, "state": result.final_state, "action": result.proposed_action}
            ),
            flush=True,
        )
        # Save progress before the next expensive case.
        output.parent.mkdir(parents=True, exist_ok=True)
        output.with_suffix(".progress.json").write_text(
            json.dumps([r.model_dump(mode="json") for r in results], indent=2)
        )
    score = summarize(results)
    commit = (
        await asyncio.to_thread(
            subprocess.check_output, ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        )
    ).strip()
    dirty = bool(
        (
            await asyncio.to_thread(
                subprocess.check_output, ["git", "status", "--porcelain"], cwd=ROOT, text=True
            )
        ).strip()
    )
    provenance: JsonDict = {
        "started_at": started.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "manifest_hash": digest(manifest),
        "manifest": str(manifest.relative_to(ROOT))
        if manifest.is_relative_to(ROOT)
        else str(manifest),
        "python": platform.python_version(),
        "machine": platform.platform(),
        "architecture": platform.machine(),
        "git_commit": commit,
        "dirty": dirty,
        "uv_lock_hash": digest(ROOT / "uv.lock"),
        "web_lock_hash": digest(ROOT / "web/package-lock.json"),
        "request_schema_hash": canonical_hash(REQUEST.json_schema()),
        "model_protocol_version": MODEL_PROTOCOL_VERSION if mode == "model" else None,
        "explanation_renderer_version": EXPLANATION_VERSION if mode == "model" else None,
        "system_instruction_hash": canonical_hash(system_instruction())
        if mode == "model"
        else None,
        "temperature": 0,
        "max_output_tokens": 768,
        "case_deadline_seconds": 120,
        "runtime_root": str(root),
        "cost_estimate": None,
        "missing_evidence": ["Human review of model claims"] if mode == "model" else [],
    }
    if mode == "model":
        provenance["protocol_definition"] = protocol_definition()
        provenance["protocol_definition_hash"] = canonical_hash(protocol_definition())
        provenance["generated_claims"] = summarize_claims([result.trace for result in results])
    gates: JsonDict = {
        "valid_actions": score.valid_action_count >= 27,
        "correct_workflow": score.correct_workflow_count >= 27,
        "authorized_completion": score.authorized_completion_count >= 22,
        "safety": score.unapproved_writes == 0 and score.duplicate_effects == 0,
        "claims_review": score.claims_review_complete and score.unsupported_claims == 0,
    }
    if frozen.version >= 5:
        gates.update(strict_quality_gates(score))
    if mode == "model":
        claims = summarize_claims([result.trace for result in results])
        gates["generated_claims"] = claims["fully_correct_cases"] == len(results)
    report = EvaluationReport(
        mode=mode, provenance=provenance, results=results, score=score, gates=gates
    )
    output.write_text(report.model_dump_json(indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", choices=["fixture", "model"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(evaluate(args.manifest.resolve(), args.mode, args.output.resolve()))


if __name__ == "__main__":
    main()
