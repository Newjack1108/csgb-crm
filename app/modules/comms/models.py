from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.db import Base


class ContactChannel(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"
    PHONE = "phone"
    NOTE = "note"
    SYSTEM = "system"
    AUTOMATION = "automation"


class ContactDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class ContactEvent(Base):
    __tablename__ = "contact_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    channel = Column(SQLEnum(ContactChannel), nullable=False)
    direction = Column(SQLEnum(ContactDirection), nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    meta = Column(JSONB, nullable=True)  # Store additional metadata like Twilio SID, status, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="contact_events")
    lead = relationship("Lead", back_populates="contact_events")
