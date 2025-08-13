from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class TrackingCreate(BaseModel):
    noc_tracking_number: UUID
    guest_id: UUID
    status: str
    note: Optional[str] = None
    is_guest_application: bool = True


class TrackingResponse(BaseModel):
    id: UUID
    noc_tracking_number: UUID
    guest_id: UUID
    status: str
    note: Optional[str]
    is_guest_application: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
