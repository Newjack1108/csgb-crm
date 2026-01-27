from typing import List, Optional, Dict, Any
from app.modules.leads.models import Lead


def compute_missing_fields(lead: Lead) -> List[str]:
    """
    Compute missing fields required for qualification.
    Checks for:
    - name
    - phone_or_email (at least one)
    - postcode
    - product_interest
    - timeframe
    """
    missing = []
    
    # Check name
    if not lead.name or not lead.name.strip():
        missing.append("name")
    
    # Check phone or email (at least one required)
    if not lead.phone and not lead.email:
        missing.append("phone_or_email")
    
    # Check postcode (from raw_payload)
    postcode = None
    if lead.raw_payload and isinstance(lead.raw_payload, dict):
        postcode = lead.raw_payload.get("postcode")
    
    if not postcode or not str(postcode).strip():
        missing.append("postcode")
    
    # Check product_interest (from raw_payload)
    product_interest = None
    if lead.raw_payload and isinstance(lead.raw_payload, dict):
        product_interest = lead.raw_payload.get("product_interest")
    
    if not product_interest or not str(product_interest).strip():
        missing.append("product_interest")
    
    # Check timeframe (from raw_payload)
    timeframe = None
    if lead.raw_payload and isinstance(lead.raw_payload, dict):
        timeframe = lead.raw_payload.get("timeframe")
    
    if not timeframe or not str(timeframe).strip():
        missing.append("timeframe")
    
    return missing
