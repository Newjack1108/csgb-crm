from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.modules.leads.models import LeadSource, LeadStatus
from app.modules.customers.schemas import CustomerSummary


class LeadBase(BaseModel):
    source: LeadSource
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None


class LeadCreate(LeadBase):
    external_id: Optional[str] = None  # For webhook deduplication


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    qualification_notes: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None


class Lead(LeadBase):
    id: UUID
    status: LeadStatus
    customer_id: Optional[UUID] = None
    missing_fields: Optional[List[str]] = None
    qualification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadDetail(BaseModel):
    """Lead detail with customer and timeline"""
    lead: Lead
    customer: Optional[CustomerSummary] = None
    timeline: List["ContactEventSummary"] = []

    class Config:
        from_attributes = True


# Forward reference resolution
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


class ContactEventSummary(BaseModel):
    """Lightweight contact event for timeline"""
    id: UUID
    channel: str
    direction: str
    subject: Optional[str] = None
    body: str
    created_at: datetime

    class Config:
        from_attributes = True


class LeadInboxItem(BaseModel):
    """Lead item for inbox view"""
    id: UUID
    source: LeadSource
    status: LeadStatus
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    missing_fields: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QualifyResponse(BaseModel):
    lead_id: UUID
    opportunity_id: UUID
    message: str


class RequestInfoResponse(BaseModel):
    lead_id: UUID
    status: LeadStatus
    missing_fields: List[str]
    message: str
