from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.db import get_db
from app.modules.automation.service import start_qualification_chase
from app.modules.leads.service import request_info_for_lead

router = APIRouter()


@router.post("/leads/{lead_id}/chase")
async def trigger_qualification_chase(
    lead_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Manually trigger qualification chase for a lead.
    This endpoint is optional - the main trigger is via /leads/{lead_id}/request-info
    """
    try:
        # Ensure lead is in NEEDS_INFO status
        lead = request_info_for_lead(db=db, lead_id=lead_id)
        
        # Start automation
        start_qualification_chase(db=db, lead_id=lead_id)
        
        return {
            "success": True,
            "lead_id": str(lead_id),
            "message": "Qualification chase started",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
