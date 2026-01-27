from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.modules.comms.models import ContactEvent, ContactChannel, ContactDirection
from app.modules.comms.schemas import ContactEventCreate
from app.modules.leads.service import get_lead_detail
from app.modules.customers.service import find_or_create_customer
from app.modules.comms.providers.twilio_sms import get_twilio_provider
from app.core.utils import normalize_phone_to_e164, extract_uk_postcode


def send_sms_to_lead(db: Session, lead_id: UUID, message: str) -> dict:
    """
    Send SMS to a lead.
    Returns dict with success, message_sid, status, error.
    """
    lead = get_lead_detail(db, lead_id)
    if not lead:
        return {"success": False, "error": "Lead not found"}
    
    if not lead.phone:
        return {"success": False, "error": "Lead has no phone number"}
    
    # Get customer for logging
    customer_id = lead.customer_id
    
    # Send SMS
    try:
        provider = get_twilio_provider()
        result = provider.send_sms(to_number=lead.phone, body=message)
        
        if result.get("error"):
            return {"success": False, "error": result["error"]}
        
        # Log contact event
        event = ContactEvent(
            customer_id=customer_id,
            lead_id=lead_id,
            channel=ContactChannel.SMS,
            direction=ContactDirection.OUTBOUND,
            body=message,
            meta={
                "twilio_sid": result.get("sid"),
                "twilio_status": result.get("status"),
            },
        )
        db.add(event)
        db.commit()
        
        return {
            "success": True,
            "message_sid": result.get("sid"),
            "status": result.get("status"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_inbound_sms(
    db: Session,
    from_number: str,
    body: str,
    message_sid: str,
) -> dict:
    """
    Handle inbound SMS webhook from Twilio.
    - Normalize phone to E.164
    - Find or create customer
    - Create lead if needed
    - Log contact event
    - Attempt to capture missing fields
    """
    # Normalize phone
    normalized_phone = normalize_phone_to_e164(from_number)
    if not normalized_phone:
        return {"success": False, "error": "Invalid phone number"}
    
    # Find or create customer
    customer = find_or_create_customer(db=db, phone=normalized_phone)
    
    # Find active lead needing info
    from app.modules.leads.models import Lead, LeadStatus, LeadSource
    from app.modules.leads.scoring import compute_missing_fields
    
    stmt = (
        select(Lead)
        .where(
            Lead.customer_id == customer.id,
            Lead.status == LeadStatus.NEEDS_INFO,
        )
        .order_by(Lead.created_at.desc())
        .limit(1)
    )
    lead = db.execute(stmt).scalar_one_or_none()
    
    # If no active lead, create one
    if not lead:
        lead = Lead(
            source=LeadSource.OTHER,
            status=LeadStatus.NEW,
            customer_id=customer.id,
            phone=normalized_phone,
        )
        lead.missing_fields = compute_missing_fields(lead)
        if lead.missing_fields:
            lead.status = LeadStatus.NEEDS_INFO
        db.add(lead)
        db.commit()
        db.refresh(lead)
    
    # Attempt to capture missing fields
    updated_fields = False
    if lead.raw_payload is None:
        lead.raw_payload = {}
    
    # Check for postcode
    if lead.missing_fields and "postcode" in lead.missing_fields:
        postcode = extract_uk_postcode(body)
        if postcode:
            if lead.raw_payload is None:
                lead.raw_payload = {}
            lead.raw_payload["postcode"] = postcode
            updated_fields = True
    
    # Recompute missing fields if we updated
    if updated_fields:
        from app.modules.leads.scoring import compute_missing_fields
        lead.missing_fields = compute_missing_fields(lead)
        # If no more missing fields, set status to NEW
        if not lead.missing_fields:
            lead.status = LeadStatus.NEW
        db.commit()
    
    # Log contact event
    event = ContactEvent(
        customer_id=customer.id,
        lead_id=lead.id,
        channel=ContactChannel.SMS,
        direction=ContactDirection.INBOUND,
        body=body,
        meta={"twilio_message_sid": message_sid},
    )
    db.add(event)
    db.commit()
    
    return {"success": True, "lead_id": str(lead.id), "customer_id": str(customer.id)}


def get_timeline_events(
    db: Session,
    customer_id: Optional[UUID] = None,
    lead_id: Optional[UUID] = None,
    limit: int = 100,
) -> list[ContactEvent]:
    """
    Get timeline events for a customer or lead, ordered newest first.
    """
    stmt = select(ContactEvent)
    
    conditions = []
    if customer_id:
        conditions.append(ContactEvent.customer_id == customer_id)
    if lead_id:
        conditions.append(ContactEvent.lead_id == lead_id)
    
    if conditions:
        from sqlalchemy import or_
        stmt = stmt.where(or_(*conditions))
    
    stmt = stmt.order_by(ContactEvent.created_at.desc()).limit(limit)
    
    return list(db.execute(stmt).scalars().all())


def create_contact_event(db: Session, event_data: ContactEventCreate) -> ContactEvent:
    """Create a contact event"""
    event = ContactEvent(**event_data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
