from eval.contracts import CaseResult
from eval.scoring import summarize


def test_unknown_write_is_not_success() -> None:
    result = CaseResult(
        case_id="holdout-01",
        family="uncertain_write",
        expected_action="manual_review",
        proposed_action="manual_review",
        expected_final_state="completed",
        final_state="review_required",
        approved=True,
        unapproved_writes=0,
        duplicate_effects=0,
        unsupported_claims=None,
        usage_tokens=None,
        elapsed_ms=10,
        tool_calls=3,
        tickets=1,
        annotations=0,
        expected_tickets=1,
        expected_annotations=1,
    )
    score = summarize([result])
    assert score.authorized_completion_count == 0
    assert score.usage_tokens is None
    assert score.claims_review_complete is False


def test_generated_claim_score_includes_failed_and_incomplete_cases() -> None:
    from eval.model_claims import summarize_claims

    score = summarize_claims(
        [
            {
                "assessment_diagnostics": {
                    "fields_correct": 6,
                    "fields_evaluated": 6,
                    "reason_supported": True,
                },
                "model_assessment": {"a": True},
            },
            {
                "assessment_diagnostics": {
                    "fields_correct": 5,
                    "fields_evaluated": 6,
                    "reason_supported": False,
                },
                "status": "failed",
            },
            {
                "status": "failed",
                "model_assessment": {"order_in_transit": True},
                "assessment_diagnostics": {
                    "fields_correct": 1,
                    "fields_evaluated": 1,
                    "reason_supported": None,
                },
            },
        ]
    )
    assert score == {
        "fields_correct": 12,
        "fields_incorrect": 1,
        "fields_missing": 5,
        "fields_total": 18,
        "supported_reasons": 1,
        "reasons_total": 3,
        "fully_correct_cases": 1,
        "cases_total": 3,
        "complete_assessments": 2,
    }


def test_v5_gate_rejects_wrong_action_even_with_perfect_generated_claims() -> None:
    from eval.scoring import strict_quality_gates

    row = CaseResult(
        case_id="wrong-action",
        family="delay",
        expected_action="open_investigation",
        proposed_action=None,
        expected_final_state="completed",
        final_state="failed",
        approved=False,
        unapproved_writes=0,
        duplicate_effects=0,
        unsupported_claims=None,
        usage_tokens=None,
        elapsed_ms=1,
        tool_calls=3,
        tickets=0,
        annotations=0,
        expected_tickets=1,
        expected_annotations=1,
        trace={
            "assessment_diagnostics": {
                "fields_correct": 6,
                "fields_evaluated": 6,
                "reason_supported": True,
            }
        },
    )
    score = summarize([row])
    assert strict_quality_gates(score) == {
        "all_actions_correct": False,
        "all_workflows_correct": False,
        "all_authorized_completions": False,
    }
