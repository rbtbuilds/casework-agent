from datetime import datetime

from .contracts import Order, Shipment
from .policy import current_policy
from .policy_assessment import PrimaryReason
from .temporal import elapsed_microseconds, to_utc

EXPLANATION_VERSION = "validated-reason-renderer-v2"


def explain(reason: PrimaryReason, order: Order, shipment: Shipment, as_of: datetime) -> str:
    detail = _detail(reason, order, shipment, as_of)
    return detail if reason == "all_pass" else "One reason for manual review: " + detail


def _detail(reason: PrimaryReason, order: Order, shipment: Shipment, as_of: datetime) -> str:
    threshold = current_policy().delay_hours * 3_600_000_000
    last = shipment.last_event_at
    if reason == "order_in_transit":
        return f"Order status is '{order.status}'; investigation requires 'in_transit'."
    if reason == "shipment_delayed":
        return f"Shipment status is '{shipment.status}'; investigation requires 'delayed'."
    if reason == "no_policy_exception":
        return "The order records a policy exception; this requires manual review."
    if reason == "no_conflicting_or_terminal_events":
        return "Carrier evidence reports a conflict or a delivered/cancelled event."
    if reason == "timestamps_known_and_consistent":
        if last is None:
            return "The last-event timestamp is missing; event age cannot be established."
        if last.tzinfo is None:
            return (
                f"The last-event timestamp {last.isoformat()} has no timezone; "
                "UTC time and event age are unknown."
            )
        if as_of.tzinfo is None:
            return "The case clock has no timezone; chronology cannot be established."
        last_utc, now = to_utc(last), to_utc(as_of)
        assert last_utc is not None and now is not None
        if last_utc > now:
            return "The last event is later than the case clock; chronology is inconsistent."
        if any(event.at.tzinfo is None for event in shipment.events):
            return "A carrier event has no timezone; chronology cannot be established."
        return (
            "A carrier event is later than the last-event summary or case clock; "
            "chronology is inconsistent."
        )
    if reason == "age_at_least_48_hours":
        if last is None:
            return "Event age is unknown because the last-event timestamp is missing."
        if last.tzinfo is None:
            return f"Event age is unknown because the last-event timestamp {last.isoformat()} has no timezone."
        if as_of.tzinfo is None:
            return "Event age is unknown because the case clock has no timezone."
    assert last is not None and last.tzinfo is not None and as_of.tzinfo is not None
    age = elapsed_microseconds(as_of, last)
    assert age is not None
    if reason == "age_at_least_48_hours":
        if age < 0:
            unit = "microsecond" if age == -1 else "microseconds"
            return f"The last event is {-age} {unit} after the case clock; elapsed age is {age} {unit}."
        return f"Event age is {age} microseconds, below the {threshold}-microsecond threshold."
    return (
        "Order is 'in_transit', shipment is 'delayed', with no policy exception, "
        "conflict or terminal event. Timestamps are known and consistent. "
        f"Event age is {age} microseconds, meeting the {threshold}-microsecond threshold."
    )
