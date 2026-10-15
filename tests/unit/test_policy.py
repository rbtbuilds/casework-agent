from datetime import UTC, datetime, timedelta

import pytest

from casework_agent.contracts import Order, Shipment
from casework_agent.policy import allowed_action

NOW = datetime(2026, 10, 15, 12, tzinfo=UTC)


@pytest.mark.parametrize(
    ("hours", "want"),
    [
        (47.999, "manual_review"),
        (48, "open_investigation"),
        (72, "open_investigation"),
        (-1, "manual_review"),
    ],
)
def test_delay_boundary(hours: float, want: str) -> None:
    order = Order(order_id="o-001", shipment_id="s-001", status="in_transit")
    shipment = Shipment(
        shipment_id="s-001", status="delayed", last_event_at=NOW - timedelta(hours=hours)
    )
    assert allowed_action(order, shipment, NOW) == want


@pytest.mark.parametrize("reason", ["delivered", "missing", "conflicting", "exception"])
def test_uncertain_or_excluded_evidence_is_manual(reason: str) -> None:
    order = Order(
        order_id="o-001",
        shipment_id="s-001",
        status="delivered" if reason == "delivered" else "in_transit",
        policy_exception="refund requested" if reason == "exception" else None,
    )
    shipment = Shipment(
        shipment_id="s-001",
        status="delayed",
        last_event_at=None if reason == "missing" else NOW - timedelta(hours=72),
        conflicting_events=reason == "conflicting",
    )
    assert allowed_action(order, shipment, NOW) == "manual_review"
