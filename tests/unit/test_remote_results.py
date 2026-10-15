from pathlib import Path

import pytest

from casework_agent.config import Settings
from casework_agent.contracts import JsonDict, Operation
from casework_agent.executor import Executor
from casework_agent.repository import Repository


@pytest.mark.parametrize("kind", ["create_ticket", "annotate_order"])
@pytest.mark.parametrize("identifier", [None, "", "   "])
def test_remote_success_requires_an_explicit_usable_id(
    tmp_path: Path, kind: str, identifier: str | None
) -> None:
    ticket = kind == "create_ticket"
    body: JsonDict = (
        {
            "order_id": "o",
            "action": "manual_review",
            "queue": "human_review",
            "priority": "normal",
            "internal_note": "Fictional review.",
        }
        if ticket
        else {
            "order_id": "o",
            "ticket_id": "remote-ticket",
            "action": "manual_review",
            "expected_order_version": 1,
        }
    )
    operation = Operation.model_validate(
        {
            "case_id": "c",
            "approval_id": "a",
            "ordinal": 1 if ticket else 2,
            "kind": kind,
            "key": "saved-key",
            "request_json": body,
        }
    )
    response: JsonDict = (
        {**body, "operation_key": operation.key}
        if ticket
        else {
            "ticket_id": "remote-ticket",
            "action": "manual_review",
            "operation_key": operation.key,
        }
    )
    if identifier is not None:
        response["ticket_id" if ticket else "annotation_id"] = identifier
    with Repository.open(tmp_path / "app.sqlite3") as repo:
        executor = Executor(repo, Settings(root=tmp_path), "owner", 1)
        with pytest.raises(ValueError):
            executor.validate_success(operation, response)
