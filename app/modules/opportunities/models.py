from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, DateTime, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.db import Base


class OpportunityStage(str, enum.Enum):
    NEW = "new"
    QUOTING = "quoting"
    FOLLOWUP = "followup"
    WON = "won"
    LOST = "lost"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    stage = Column(SQLEnum(OpportunityStage), default=OpportunityStage.NEW, nullable=False)
    value_estimate = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="opportunities")
    lead = relationship("Lead", back_populates="opportunity")
