import math

from casework_agent.contracts import JsonDict

from .contracts import CaseResult, Score


def summarize(results: list[CaseResult]) -> Score:
    def correct(row: CaseResult) -> bool:
        return (
            row.final_state == row.expected_final_state
            and row.tickets == row.expected_tickets
            and row.annotations == row.expected_annotations
        )

    times = sorted(r.elapsed_ms for r in results)
    claims = all(r.unsupported_claims is not None for r in results)
    families: dict[str, JsonDict] = {
        family: {
            "count": len(rows),
            "valid_actions": sum(r.proposed_action == r.expected_action for r in rows),
            "correct_workflows": sum(correct(r) for r in rows),
        }
        for family in sorted({r.family for r in results})
        if (rows := [r for r in results if r.family == family])
    }
    return Score(
        total=len(results),
        valid_action_count=sum(r.proposed_action == r.expected_action for r in results),
        correct_workflow_count=sum(correct(r) for r in results),
        authorized_completion_count=sum(
            r.approved and r.expected_final_state == "completed" and correct(r) for r in results
        ),
        authorized_completion_denominator=sum(
            r.expected_final_state == "completed" for r in results
        ),
        unapproved_writes=sum(r.unapproved_writes for r in results),
        duplicate_effects=sum(r.duplicate_effects for r in results),
        unsupported_claims=sum(r.unsupported_claims or 0 for r in results) if claims else None,
        claims_review_complete=claims,
        unnecessary_escalations=sum(
            r.expected_action == "open_investigation" and r.proposed_action == "manual_review"
            for r in results
        ),
        investigation_denominator=sum(r.expected_action == "open_investigation" for r in results),
        usage_tokens=sum(r.usage_tokens or 0 for r in results)
        if all(r.usage_tokens is not None for r in results)
        else None,
        latency_p50_ms=times[math.ceil(len(times) * 0.5) - 1] if times else None,
        latency_p95_ms=times[math.ceil(len(times) * 0.95) - 1] if times else None,
        failures=sum(r.final_state == "failed" for r in results),
        families=families,
    )
