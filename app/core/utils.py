import re
from typing import Optional


def normalize_phone_to_e164(phone: Optional[str]) -> Optional[str]:
    """
    Normalize phone number to E.164 format.
    Minimal UK-safe normalization.
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # If it starts with +, assume it's already in E.164
    if cleaned.startswith('+'):
        return cleaned
    
    # UK number patterns
    # Remove leading 0 if present
    if cleaned.startswith('0'):
        cleaned = cleaned[1:]
    
    # If it starts with 44 (UK country code without +)
    if cleaned.startswith('44'):
        return f"+{cleaned}"
    
    # If it's 10-11 digits and doesn't start with country code, assume UK
    if len(cleaned) >= 10 and len(cleaned) <= 11:
        return f"+44{cleaned}"
    
    # If it's already 11-15 digits, assume it's a valid number without country code
    if len(cleaned) >= 11:
        return f"+{cleaned}"
    
    # Return as-is if we can't normalize
    return cleaned if cleaned else None


def extract_uk_postcode(text: Optional[str]) -> Optional[str]:
    """
    Extract UK postcode from text using regex.
    Returns the postcode if found, None otherwise.
    """
    if not text:
        return None
    
    # UK postcode pattern: AA9A 9AA or A9A 9AA or A9 9AA or AA9 9AA or A99 9AA or AA99 9AA
    pattern = r'\b([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})\b'
    match = re.search(pattern, text.upper())
    if match:
        # Normalize spacing
        postcode = match.group(1).replace(' ', '').upper()
        # Insert space before last 3 characters
        if len(postcode) > 3:
            return f"{postcode[:-3]} {postcode[-3:]}"
        return postcode
    return None
