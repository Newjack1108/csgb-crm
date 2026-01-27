from typing import Optional
from twilio.rest import Client
from twilio.request_validator import RequestValidator

from app.core.config import settings


class TwilioSMSProvider:
    def __init__(self):
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise ValueError("Twilio credentials not configured")
        
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    
    def send_sms(self, to_number: str, body: str) -> dict:
        """
        Send SMS via Twilio.
        Returns dict with 'sid' and 'status'.
        """
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.phone_number,
                to=to_number,
            )
            return {
                "sid": message.sid,
                "status": message.status,
            }
        except Exception as e:
            return {
                "sid": None,
                "status": "failed",
                "error": str(e),
            }
    
    def validate_request(self, url: str, params: dict, signature: str) -> bool:
        """
        Validate Twilio webhook request signature.
        """
        if not settings.TWILIO_WEBHOOK_VALIDATE:
            return True  # Skip validation if disabled
        
        return self.validator.validate(url, params, signature)


# Singleton instance
_twilio_provider: Optional[TwilioSMSProvider] = None


def get_twilio_provider() -> TwilioSMSProvider:
    """Get or create Twilio SMS provider instance"""
    global _twilio_provider
    if _twilio_provider is None:
        _twilio_provider = TwilioSMSProvider()
    return _twilio_provider
