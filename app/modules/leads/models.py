from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.db import Base


class LeadSource(str, enum.Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WEBSITE = "website"
    MANUAL = "manual"
    OTHER = "other"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    NEEDS_INFO = "needs_info"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(SQLEnum(LeadSource), nullable=False)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    owner_user_id = Column(UUID(as_uuid=True), nullable=True)  # Stubbed for future use
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True, index=True)  # E.164 format
    raw_payload = Column(JSONB, nullable=True)
    missing_fields = Column(JSONB, nullable=True)  # Array of strings
    qualification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="leads")
    contact_events = relationship("ContactEvent", back_populates="lead")
    opportunity = relationship("Opportunity", back_populates="lead", uselist=False)


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
