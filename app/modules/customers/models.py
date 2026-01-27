from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.db import Base


class CustomerStatus(str, enum.Enum):
    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    primary_email = Column(String, nullable=True, index=True)
    primary_phone = Column(String, nullable=True, index=True)  # E.164 format
    status = Column(SQLEnum(CustomerStatus), default=CustomerStatus.PROSPECT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    leads = relationship("Lead", back_populates="customer")
    opportunities = relationship("Opportunity", back_populates="customer")
    contact_events = relationship("ContactEvent", back_populates="customer")
