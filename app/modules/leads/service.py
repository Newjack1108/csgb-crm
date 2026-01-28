from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import hashlib
import json

from app.modules.leads.models import Lead, LeadSource, LeadStatus, IdempotencyKey
from app.modules.leads.schemas import LeadCreate, LeadUpdate
from app.modules.leads.scoring import compute_missing_fields
from app.modules.customers.service import find_or_create_customer
from app.modules.comms.models import ContactEvent, ContactChannel, ContactDirection
from app.modules.opportunities.models import Opportunity, OpportunityStage
from app.core.idempotency import check_idempotency_key, create_idempotency_key, generate_idempotency_key
from app.core.utils import normalize_phone_to_e164


def create_lead_from_webhook(
    db: Session,
    source: LeadSource,
    payload: dict,
    external_id: Optional[str] = None,
) -> tuple[Optional[Lead], bool]:
    """
    Create lead from webhook with idempotency check.
    Returns (lead, is_duplicate)
    """
    # Generate idempotency key
    if external_id:
        idempotency_key_str = generate_idempotency_key(source.value, external_id=external_id)
    else:
        # Hash payload for deduplication
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        idempotency_key_str = generate_idempotency_key(source.value, payload_hash=payload_hash)
    
    # Check idempotency
    exists, _ = check_idempotency_key(db, idempotency_key_str)
    if exists:
        # For MVP, we return None to indicate duplicate
        # In production, you might want to store the lead_id in the idempotency key metadata
        return None, True
    
    # Create idempotency key
    create_idempotency_key(db, idempotency_key_str)
    
    # Extract fields from payload
    name = payload.get("name") or payload.get("full_name")
    email = payload.get("email")
    phone = payload.get("phone") or payload.get("phone_number")
    
    # Normalize phone
    normalized_phone = normalize_phone_to_e164(phone) if phone else None
    
    # Find or create customer
    customer = find_or_create_customer(
        db=db,
        email=email,
        phone=normalized_phone,
        name=name,
    )
    
    # Create lead
    lead = Lead(
        source=source,
        name=name,
        email=email,
        phone=normalized_phone,
        customer_id=customer.id,
        raw_payload=payload,
        status=LeadStatus.NEW,
    )
    
    # Compute missing fields
    lead.missing_fields = compute_missing_fields(lead)
    
    # Set status based on missing fields
    if lead.missing_fields:
        lead.status = LeadStatus.NEEDS_INFO
    else:
        lead.status = LeadStatus.NEW
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    # Log system event
    event = ContactEvent(
        customer_id=customer.id,
        lead_id=lead.id,
        channel=ContactChannel.SYSTEM,
        direction=ContactDirection.INTERNAL,
        body=f"Lead received from {source.value}",
        meta={"source": source.value, "idempotency_key": idempotency_key_str},
    )
    db.add(event)
    db.commit()
    
    return lead, False


def create_lead_manual(
    db: Session,
    lead_data: LeadCreate,
) -> Lead:
    """Create lead manually"""
    normalized_phone = normalize_phone_to_e164(lead_data.phone) if lead_data.phone else None
    
    # Find or create customer
    customer = find_or_create_customer(
        db=db,
        email=lead_data.email,
        phone=normalized_phone,
        name=lead_data.name,
    )
    
    # Create lead
    lead = Lead(
        source=lead_data.source,
        name=lead_data.name,
        email=lead_data.email,
        phone=normalized_phone,
        customer_id=customer.id,
        raw_payload=lead_data.raw_payload,
        status=LeadStatus.NEW,
    )
    
    # Compute missing fields
    lead.missing_fields = compute_missing_fields(lead)
    
    # Set status based on missing fields
    if lead.missing_fields:
        lead.status = LeadStatus.NEEDS_INFO
    else:
        lead.status = LeadStatus.NEW
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    # Log system event
    event = ContactEvent(
        customer_id=customer.id,
        lead_id=lead.id,
        channel=ContactChannel.SYSTEM,
        direction=ContactDirection.INTERNAL,
        body=f"Lead created manually from {lead_data.source.value}",
    )
    db.add(event)
    db.commit()
    
    return lead


def get_lead_inbox(db: Session, limit: int = 100, offset: int = 0) -> List[Lead]:
    """Get leads for inbox (status NEW or NEEDS_INFO), ordered newest first"""
    # Use string literals to match database enum values (lowercase)
    stmt = (
        select(Lead)
        .where(
            or_(
                Lead.status == "new",
                Lead.status == "needs_info",
            )
        )
        .order_by(Lead.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def get_lead_detail(db: Session, lead_id: UUID) -> Optional[Lead]:
    """Get lead by ID"""
    stmt = select(Lead).where(Lead.id == lead_id)
    return db.execute(stmt).scalar_one_or_none()


def update_lead(db: Session, lead_id: UUID, lead_update: LeadUpdate) -> Optional[Lead]:
    """Update lead"""
    lead = get_lead_detail(db, lead_id)
    if not lead:
        return None
    
    update_data = lead_update.model_dump(exclude_unset=True)
    
    # Normalize phone if provided
    if "phone" in update_data and update_data["phone"]:
        update_data["phone"] = normalize_phone_to_e164(update_data["phone"])
    
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    # Recompute missing fields if relevant fields changed
    if any(field in update_data for field in ["name", "email", "phone", "raw_payload"]):
        lead.missing_fields = compute_missing_fields(lead)
        # Update status based on missing fields
        if lead.missing_fields:
            lead.status = LeadStatus.NEEDS_INFO
        elif lead.status == LeadStatus.NEEDS_INFO:
            lead.status = LeadStatus.NEW
    
    db.commit()
    db.refresh(lead)
    return lead


def qualify_lead(db: Session, lead_id: UUID) -> Optional[Opportunity]:
    """
    Qualify a lead:
    - Validate missing_fields is empty
    - Ensure customer exists
    - Create opportunity stub
    - Set lead status to QUALIFIED
    - Log system event
    """
    lead = get_lead_detail(db, lead_id)
    if not lead:
        return None
    
    # Validate missing fields
    if lead.missing_fields and len(lead.missing_fields) > 0:
        raise ValueError(f"Lead has missing fields: {lead.missing_fields}")
    
    # Ensure customer exists
    if not lead.customer_id:
        # Create customer if not exists
        customer = find_or_create_customer(
            db=db,
            email=lead.email,
            phone=lead.phone,
            name=lead.name,
        )
        lead.customer_id = customer.id
    
    # Create opportunity
    opportunity = Opportunity(
        customer_id=lead.customer_id,
        lead_id=lead.id,
        stage=OpportunityStage.NEW,
        value_estimate=None,
    )
    db.add(opportunity)
    
    # Update lead status
    lead.status = LeadStatus.QUALIFIED
    
    # Log system event
    event = ContactEvent(
        customer_id=lead.customer_id,
        lead_id=lead.id,
        channel=ContactChannel.SYSTEM,
        direction=ContactDirection.INTERNAL,
        body="Lead qualified and moved to sales",
        meta={"opportunity_id": str(opportunity.id)},
    )
    db.add(event)
    
    db.commit()
    db.refresh(opportunity)
    return opportunity


def request_info_for_lead(db: Session, lead_id: UUID) -> Lead:
    """
    Request info for a lead:
    - Set status to NEEDS_INFO if not already
    - Ensure missing_fields is computed
    - Returns the lead
    """
    lead = get_lead_detail(db, lead_id)
    if not lead:
        raise ValueError(f"Lead {lead_id} not found")
    
    # Compute missing fields if not already set
    if not lead.missing_fields:
        lead.missing_fields = compute_missing_fields(lead)
    
    # Set status to NEEDS_INFO
    if lead.status != LeadStatus.NEEDS_INFO:
        lead.status = LeadStatus.NEEDS_INFO
    
    db.commit()
    db.refresh(lead)
    return lead
