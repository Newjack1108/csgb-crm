from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.modules.comms.service import send_sms_to_lead, handle_inbound_sms
from app.modules.comms.schemas import SendSMSRequest, SendSMSResponse
from app.modules.comms.providers.twilio_sms import get_twilio_provider
from app.core.config import settings

router = APIRouter()


@router.post("/sms/send", response_model=SendSMSResponse)
async def send_sms(
    request: SendSMSRequest,
    db: Session = Depends(get_db),
):
    """Send SMS to a lead"""
    result = send_sms_to_lead(db=db, lead_id=request.lead_id, message=request.message)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send SMS"))
    
    return SendSMSResponse(
        success=True,
        message_sid=result.get("message_sid"),
        status=result.get("status"),
    )


@router.post("/webhooks/twilio/sms", include_in_schema=False)
async def twilio_sms_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Twilio SMS inbound webhook.
    Validates signature if enabled, processes inbound SMS.
    """
    # Get form data
    form_data = await request.form()
    from_number = form_data.get("From", "")
    body = form_data.get("Body", "")
    message_sid = form_data.get("MessageSid", "")
    
    # Validate signature if enabled
    if settings.TWILIO_WEBHOOK_VALIDATE:
        signature = request.headers.get("X-Twilio-Signature", "")
        url = str(request.url)
        # Convert form data to dict for validation
        params = dict(form_data)
        
        try:
            provider = get_twilio_provider()
            if not provider.validate_request(url, params, signature):
                raise HTTPException(status_code=403, detail="Invalid Twilio signature")
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"Signature validation failed: {str(e)}")
    
    # Handle inbound SMS
    result = handle_inbound_sms(
        db=db,
        from_number=from_number,
        body=body,
        message_sid=message_sid,
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to process SMS"))
    
    # Return 200 OK (TwiML not required for MVP)
    return {"status": "ok", "message": "SMS processed"}
