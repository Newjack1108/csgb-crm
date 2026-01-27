from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.modules.comms.models import ContactChannel, ContactDirection


class SendSMSRequest(BaseModel):
    lead_id: UUID
    message: str


class SendSMSResponse(BaseModel):
    success: bool
    message_sid: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


class ContactEventCreate(BaseModel):
    customer_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    channel: ContactChannel
    direction: ContactDirection
    subject: Optional[str] = None
    body: str
    meta: Optional[Dict[str, Any]] = None


class ContactEvent(ContactEventCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
