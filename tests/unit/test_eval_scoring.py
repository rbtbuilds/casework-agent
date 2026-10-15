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
