import asyncio
import json
from datetime import timedelta
from pathlib import Path

import pytest

from casework_agent.agent import AgentContext, AgentValidationError
from casework_agent.contracts import JsonDict, Shipment
from casework_agent.hashing import canonical_hash
from casework_agent.model_adapter import (
    ChatMessage,
    LocalModelAdapter,
    ModelReply,
    policy_check_inputs,
)
from casework_agent.policy_assessment import PolicyAssessment
from tests.unit.test_model_claims import NOW, proposal_body, recorded_tools


class StagedClient:
    def __init__(self, body: JsonDict) -> None:
        self.body = body
        self.requests: list[tuple[list[ChatMessage], JsonDict | None]] = []
        self.condition = 0

    async def complete(
        self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
    ) -> ModelReply:
        self.requests.append((messages.copy(), response_schema))
        if response_schema and "passes" in str(response_schema.get("properties", {})):
            field = list(PolicyAssessment.model_fields)[self.condition]
            self.condition += 1
            values = self.body["assessment"]
            assert isinstance(values, dict)
            return ModelReply(
                text=json.dumps({"passes": values[field]}), input_tokens=10, output_tokens=5
            )
        return ModelReply(
            text=json.dumps({k: v for k, v in self.body.items() if k != "assessment"}),
            input_tokens=10,
            output_tokens=5,
        )


async def test_conditions_are_isolated_and_decision_gets_unmodified_model_answers(
    tmp_path: Path,
) -> None:
    tools = recorded_tools(
        tmp_path,
        Shipment(shipment_id="shipment", status="delayed", last_event_at=NOW - timedelta(hours=60)),
    )
    context = AgentContext(case_id="case", order_id="order", as_of=NOW)
    body = proposal_body(tools)
    values = body["assessment"]
    assert isinstance(values, dict)
    values["shipment_delayed"] = False
    client = StagedClient(body)
    adapter = LocalModelAdapter(client)
    try:
        with pytest.raises(AgentValidationError, match="assessment_mismatch"):
            await adapter.propose(context, tools)
        assert len(client.requests) == 7
        groups = policy_check_inputs(context, tools)
        for (messages, schema), (_field, group) in zip(
            client.requests[:6], groups.items(), strict=True
        ):
            assert len(messages) == 2
            assert json.loads(messages[1].content) == group
            assert "expected_action" not in messages[0].content
            assert schema and "enum" not in json.dumps(schema)
        final = json.loads(client.requests[-1][0][1].content)
        assert final == {"MODEL_ASSESSMENT": values, "evidence_ids": [e.id for e in tools.evidence]}
        assert adapter.usage_tokens == 105
        assert len(adapter.inference_calls) == 7
        for ordinal, call in enumerate(adapter.inference_calls, 1):
            assert call["ordinal"] == ordinal
            assert call["schema_hash"] == canonical_hash(call["schema"])
            assert call["status"] == "received" and call["reply"]
        assert [call["field"] for call in adapter.inference_calls[:-1]] == list(groups)
        assert adapter.inference_calls[-1]["phase"] == "decision"
    finally:
        await tools.close()


@pytest.mark.parametrize("field", list(PolicyAssessment.model_fields))
async def test_every_false_claim_fails_even_with_correct_action(tmp_path: Path, field: str) -> None:
    tools = recorded_tools(
        tmp_path,
        Shipment(shipment_id="shipment", status="delayed", last_event_at=NOW - timedelta(hours=60)),
    )
    body = proposal_body(tools)
    values = body["assessment"]
    assert isinstance(values, dict)
    values[field] = False
    client = StagedClient(body)
    adapter = LocalModelAdapter(client)
    try:
        with pytest.raises(AgentValidationError, match="assessment_mismatch"):
            await adapter.propose(AgentContext(case_id="case", order_id="order", as_of=NOW), tools)
        assert adapter.assessment_diagnostics["mismatched_fields"] == [field]
        assert len(client.requests) == 7
    finally:
        await tools.close()


@pytest.mark.parametrize("stalled_phase", ["condition", "decision"])
async def test_later_timeout_preserves_partial_request_trace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stalled_phase: str
) -> None:
    import casework_agent.model_adapter as module

    tools = recorded_tools(
        tmp_path,
        Shipment(shipment_id="shipment", status="delayed", last_event_at=NOW - timedelta(hours=60)),
    )

    class Stalled(StagedClient):
        async def complete(
            self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
        ) -> ModelReply:
            if len(self.requests) == (2 if stalled_phase == "condition" else 6):
                await asyncio.sleep(5)
            return await super().complete(messages, response_schema=response_schema)

    adapter = LocalModelAdapter(Stalled(proposal_body(tools)))
    monkeypatch.setattr(module, "CASE_DEADLINE_SECONDS", 0.05)
    try:
        with pytest.raises(AgentValidationError, match="model_deadline"):
            await adapter.propose(AgentContext(case_id="case", order_id="order", as_of=NOW), tools)
        assert len(adapter.inference_calls) == (3 if stalled_phase == "condition" else 7)
        assert adapter.inference_calls[-1]["status"] == "cancelled"
        assert adapter.inference_calls[-1]["reply"] is None
        assert adapter.inference_calls[0]["reply"] is not None
        assert adapter.usage_tokens is None
        assert adapter.assessment_diagnostics["fields_correct"] == (
            2 if stalled_phase == "condition" else 6
        )
        assert adapter.assessment_diagnostics["fields_evaluated"] == (
            2 if stalled_phase == "condition" else 6
        )
        assert adapter.assessment_diagnostics["reason_supported"] is None
    finally:
        await tools.close()


async def test_syntax_repair_is_global_and_keeps_original_failed_replies(tmp_path: Path) -> None:
    tools = recorded_tools(
        tmp_path,
        Shipment(shipment_id="shipment", status="delayed", last_event_at=NOW - timedelta(hours=60)),
    )

    class Broken(StagedClient):
        attempts = 0

        async def complete(
            self, messages: list[ChatMessage], *, response_schema: JsonDict | None = None
        ) -> ModelReply:
            self.attempts += 1
            if self.attempts in (1, 3):
                return ModelReply(text='{"passes":"yes"}')
            return await super().complete(messages, response_schema=response_schema)

    client = Broken(proposal_body(tools))
    adapter = LocalModelAdapter(client)
    try:
        with pytest.raises(AgentValidationError, match="invalid_model_output"):
            await adapter.propose(AgentContext(case_id="case", order_id="order", as_of=NOW), tools)
        assert len(adapter.inference_calls) == 3
        assert adapter.inference_calls[1]["repair_of"] == 1
        assert adapter.inference_calls[0]["reply"] == adapter.inference_calls[2]["reply"]
        assert adapter.model_assessment == {"order_in_transit": True}
        assert "expected" not in json.dumps(adapter.inference_calls[1]["messages"])
    finally:
        await tools.close()
