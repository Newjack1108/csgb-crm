from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from typing import Optional
from uuid import UUID

from app.modules.customers.models import Customer, CustomerStatus
from app.modules.customers.schemas import CustomerCreate, CustomerUpdate
from app.core.utils import normalize_phone_to_e164


def find_or_create_customer(
    db: Session,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None,
) -> Customer:
    """
    Find customer by phone first, then email.
    If not found, create a new customer.
    Enrich customer fields if missing.
    """
    # Normalize phone to E.164
    normalized_phone = normalize_phone_to_e164(phone) if phone else None
    
    # Try to find by phone first
    if normalized_phone:
        stmt = select(Customer).where(Customer.primary_phone == normalized_phone)
        customer = db.execute(stmt).scalar_one_or_none()
        if customer:
            # Enrich if needed
            if not customer.primary_email and email:
                customer.primary_email = email
            if not customer.name and name:
                customer.name = name
            db.commit()
            db.refresh(customer)
            return customer
    
    # Try to find by email
    if email:
        stmt = select(Customer).where(Customer.primary_email == email)
        customer = db.execute(stmt).scalar_one_or_none()
        if customer:
            # Enrich if needed
            if not customer.primary_phone and normalized_phone:
                customer.primary_phone = normalized_phone
            if not customer.name and name:
                customer.name = name
            db.commit()
            db.refresh(customer)
            return customer
    
    # Create new customer
    customer = Customer(
        name=name,
        primary_email=email,
        primary_phone=normalized_phone,
        status=CustomerStatus.PROSPECT,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: UUID) -> Optional[Customer]:
    """Get customer by ID"""
    stmt = select(Customer).where(Customer.id == customer_id)
    return db.execute(stmt).scalar_one_or_none()


def update_customer(db: Session, customer_id: UUID, customer_update: CustomerUpdate) -> Optional[Customer]:
    """Update customer"""
    customer = get_customer(db, customer_id)
    if not customer:
        return None
    
    update_data = customer_update.model_dump(exclude_unset=True)
    
    # Normalize phone if provided
    if "primary_phone" in update_data and update_data["primary_phone"]:
        update_data["primary_phone"] = normalize_phone_to_e164(update_data["primary_phone"])
    
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer
