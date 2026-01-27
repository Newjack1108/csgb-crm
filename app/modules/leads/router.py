from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.db import get_db
from app.modules.leads.service import (
    create_lead_from_webhook,
    create_lead_manual,
    get_lead_inbox,
    get_lead_detail,
    update_lead,
    qualify_lead,
    request_info_for_lead,
)
from app.modules.leads.schemas import (
    LeadCreate,
    LeadUpdate,
    Lead,
    LeadDetail,
    LeadInboxItem,
    QualifyResponse,
    RequestInfoResponse,
)
from app.modules.leads.models import LeadSource
from app.modules.comms.service import get_timeline_events
from app.modules.customers.schemas import CustomerSummary
from app.modules.customers.service import get_customer

router = APIRouter()


@router.post("/webhook/{source}", response_model=dict)
async def webhook_lead_intake(
    source: LeadSource,
    payload: dict,
    external_id: str = Query(None, alias="external_id"),
    db: Session = Depends(get_db),
):
    """
    Webhook endpoint for lead intake.
    Supports idempotency via external_id query parameter or payload hash.
    """
    lead, is_duplicate = create_lead_from_webhook(
        db=db,
        source=source,
        payload=payload,
        external_id=external_id,
    )
    
    if is_duplicate:
        return {"duplicate": True, "message": "Lead already processed"}
    
    return {
        "duplicate": False,
        "lead_id": str(lead.id),
        "status": lead.status.value,
        "missing_fields": lead.missing_fields or [],
    }


@router.post("/", response_model=Lead)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
):
    """Create a lead manually"""
    return create_lead_manual(db=db, lead_data=lead_data)


@router.get("/inbox", response_model=List[LeadInboxItem])
async def get_inbox(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get lead inbox (status NEW or NEEDS_INFO), ordered newest first"""
    leads = get_lead_inbox(db=db, limit=limit, offset=offset)
    return leads


@router.get("/{lead_id}", response_model=LeadDetail)
async def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
):
    """Get lead detail with customer and timeline"""
    lead = get_lead_detail(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get customer summary if linked
    customer_summary = None
    if lead.customer_id:
        customer = get_customer(db=db, customer_id=lead.customer_id)
        if customer:
            customer_summary = CustomerSummary.model_validate(customer)
    
    # Get timeline events
    timeline_events = get_timeline_events(
        db=db,
        customer_id=lead.customer_id,
        lead_id=lead.id,
    )
    
    # Convert to summary format
    from app.modules.leads.schemas import ContactEventSummary
    timeline = [ContactEventSummary.model_validate(event) for event in timeline_events]
    
    return LeadDetail(
        lead=lead,
        customer=customer_summary,
        timeline=timeline,
    )


@router.patch("/{lead_id}", response_model=Lead)
async def update_lead_endpoint(
    lead_id: UUID,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
):
    """Update a lead"""
    lead = update_lead(db=db, lead_id=lead_id, lead_update=lead_update)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/qualify", response_model=QualifyResponse)
async def qualify_lead_endpoint(
    lead_id: UUID,
    db: Session = Depends(get_db),
):
    """Qualify a lead (creates opportunity)"""
    try:
        opportunity = qualify_lead(db=db, lead_id=lead_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return QualifyResponse(
            lead_id=lead_id,
            opportunity_id=opportunity.id,
            message="Lead qualified and opportunity created",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{lead_id}/request-info", response_model=RequestInfoResponse)
async def request_info(
    lead_id: UUID,
    db: Session = Depends(get_db),
):
    """Request info for a lead (triggers automation)"""
    try:
        lead = request_info_for_lead(db=db, lead_id=lead_id)
        
        # Trigger automation (this will be handled by the automation service)
        from app.modules.automation.service import start_qualification_chase
        start_qualification_chase(db=db, lead_id=lead_id)
        
        return RequestInfoResponse(
            lead_id=lead_id,
            status=lead.status,
            missing_fields=lead.missing_fields or [],
            message="Info request initiated",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
