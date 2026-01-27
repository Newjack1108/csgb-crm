from rq import get_current_job
from typing import Optional
import os
import sys

# Add parent directory to path for imports
# This ensures we can import app modules when running as a script
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.core.db import SessionLocal
from app.modules.leads.service import get_lead_detail
from app.modules.leads.models import LeadStatus
from app.modules.comms.service import send_sms_to_lead
from app.modules.comms.providers.twilio_sms import get_twilio_provider


def send_missing_info_sms(lead_id: str):
    """
    RQ job to send SMS requesting missing information.
    """
    db = SessionLocal()
    try:
        from uuid import UUID
        lead_uuid = UUID(lead_id)
        lead = get_lead_detail(db, lead_uuid)
        
        if not lead:
            print(f"Lead {lead_id} not found")
            return
        
        # Check if lead still needs info
        if lead.status != LeadStatus.NEEDS_INFO:
            print(f"Lead {lead_id} no longer needs info (status: {lead.status})")
            return
        
        # Check if lead has phone
        if not lead.phone:
            print(f"Lead {lead_id} has no phone number")
            return
        
        # Construct SMS message
        missing_fields = lead.missing_fields or []
        if not missing_fields:
            print(f"Lead {lead_id} has no missing fields")
            return
        
        # Build message
        message_parts = ["Hi, we need some additional information:"]
        field_messages = {
            "name": "Your name",
            "phone_or_email": "Your phone number or email",
            "postcode": "Your postcode",
            "product_interest": "What product/service you're interested in",
            "timeframe": "When you're looking to proceed",
        }
        
        for field in missing_fields:
            if field in field_messages:
                message_parts.append(f"- {field_messages[field]}")
        
        message_parts.append("\nPlease reply with this information. Thank you!")
        message = "\n".join(message_parts)
        
        # Send SMS
        result = send_sms_to_lead(db=db, lead_id=lead_uuid, message=message)
        
        if result.get("success"):
            print(f"Sent missing info SMS to lead {lead_id}")
        else:
            print(f"Failed to send SMS to lead {lead_id}: {result.get('error')}")
    
    except Exception as e:
        print(f"Error in send_missing_info_sms for lead {lead_id}: {str(e)}")
        raise
    finally:
        db.close()
