from datetime import datetime, timedelta
from typing import Literal

from pydantic import StrictBool

from .contracts import Order, Shipment, StrictModel
from .policy import current_policy
from .temporal import to_utc

type PrimaryReason = Literal[
    "order_in_transit",
    "shipment_delayed",
    "no_policy_exception",
    "no_conflicting_or_terminal_events",
    "timestamps_known_and_consistent",
    "age_at_least_48_hours",
    "all_pass",
]


class PolicyAssessment(StrictModel):
    order_in_transit: StrictBool
    shipment_delayed: StrictBool
    no_policy_exception: StrictBool
    no_conflicting_or_terminal_events: StrictBool
    timestamps_known_and_consistent: StrictBool
    age_at_least_48_hours: StrictBool


def assess_policy(order: Order, shipment: Shipment, as_of: datetime) -> PolicyAssessment:
    last, now = to_utc(shipment.last_event_at), to_utc(as_of)
    events = [to_utc(event.at) for event in shipment.events]
    known = last is not None and now is not None
    consistent = bool(
        last is not None
        and now is not None
        and last <= now
        and all(event is not None and event <= last and event <= now for event in events)
    )
    return PolicyAssessment(
        order_in_transit=order.status == "in_transit",
        shipment_delayed=shipment.status == "delayed",
        no_policy_exception=not order.policy_exception,
        no_conflicting_or_terminal_events=not shipment.conflicting_events
        and not any(event.code.lower() in {"delivered", "cancelled"} for event in shipment.events),
        timestamps_known_and_consistent=consistent,
        age_at_least_48_hours=bool(
            known
            and last is not None
            and now is not None
            and now - last >= timedelta(hours=current_policy().delay_hours)
        ),
    )


def supports_reason(assessment: PolicyAssessment, reason: PrimaryReason) -> bool:
    checks = assessment.model_dump()
    return all(checks.values()) if reason == "all_pass" else checks[reason] is False
