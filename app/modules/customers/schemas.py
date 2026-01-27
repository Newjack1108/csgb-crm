from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.modules.customers.models import CustomerStatus


class CustomerBase(BaseModel):
    name: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    status: CustomerStatus = CustomerStatus.PROSPECT


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    status: Optional[CustomerStatus] = None


class Customer(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    """Lightweight customer summary for lead detail view"""
    id: UUID
    name: Optional[str] = None
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None
    status: CustomerStatus

    class Config:
        from_attributes = True
