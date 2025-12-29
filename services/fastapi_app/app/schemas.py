from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from uuid import UUID

EventType = Literal["impression", "click", "like", "save", "hide", "share"]

class EventIn(BaseModel):
    type: EventType
    item_id: UUID
    ts: datetime
    dwell_ms: Optional[int] = Field(default=None, ge=0)
    rank: Optional[int] = Field(default=None, ge=1)

class EventsIn(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    session_id: Optional[str] = Field(default=None, max_length=128)
    idempotency_key: str = Field(min_length=8, max_length=256)
    events: List[EventIn] = Field(min_length=1, max_length=500)
    context: Dict[str, Any] = Field(default_factory=dict)
    variant: Optional[str] = Field(default=None, max_length=64)

class EventsOut(BaseModel):
    accepted: int
    deduped: bool
