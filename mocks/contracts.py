from typing import Literal

from pydantic import Field

from casework_agent.contracts import Action, Queue, StrictModel


class TicketCreate(StrictModel):
    order_id: str
    action: Action
    queue: Queue
    priority: Literal["normal"]
    internal_note: str = Field(min_length=1,max_length=500)

class AnnotationCreate(StrictModel):
    order_id: str
    ticket_id: str
    action: Action
    expected_order_version: int = Field(ge=1)
