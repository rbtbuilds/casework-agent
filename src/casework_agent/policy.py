from datetime import datetime, timedelta

from .contracts import (
    Action,
    AgentDecision,
    AnnotationIntent,
    Order,
    Policy,
    Shipment,
    TicketIntent,
)
from .hashing import canonical_hash

RULES=["Only in-transit delayed orders with >=48h since last event and no conflicting/delivered evidence or policy exception may open an investigation.","All other valid evidence escalates to manual review.","No refund,payment,customer contact or delivery promise. Fictional internal action only."]

def current_policy() -> Policy:
    value={"version":"delivery-v1","delay_hours":48,"approval_ttl_seconds":900,"rules":RULES}
    return Policy.model_validate({**value,"hash":canonical_hash(value)})

def allowed_action(order: Order,shipment: Shipment,as_of: datetime) -> Action:
    if (order.status!="in_transit" or shipment.status!="delayed" or order.policy_exception
        or shipment.conflicting_events or shipment.last_event_at is None
        or shipment.shipment_id!=order.shipment_id
        or any(e.code.lower() in {"delivered","cancelled"} for e in shipment.events)):
        return "manual_review"
    if shipment.last_event_at.tzinfo is None or as_of.tzinfo is None:return "manual_review"
    return "open_investigation" if as_of-shipment.last_event_at>=timedelta(hours=48) else "manual_review"

def compile_intents(decision: AgentDecision,order: Order) -> tuple[TicketIntent,AnnotationIntent]:
    return (TicketIntent(order_id=order.order_id,action=decision.action,queue="delivery_investigation" if decision.action=="open_investigation" else "human_review",internal_note=decision.draft_note),AnnotationIntent(order_id=order.order_id,action=decision.action,expected_order_version=order.version))
