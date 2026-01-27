from sqlalchemy.orm import Session
from uuid import UUID
from datetime import timedelta

from app.core.config import settings
from redis import Redis
from rq import Queue

# Initialize Redis connection and queue
redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue("default", connection=redis_conn)


def start_qualification_chase(db: Session, lead_id: UUID):
    """
    Start qualification chase automation for a lead.
    - Enqueues immediate SMS
    - Enqueues follow-up SMS in 4 hours
    """
    from app.modules.automation.jobs import send_missing_info_sms
    
    # Enqueue immediate job
    queue.enqueue(
        send_missing_info_sms,
        str(lead_id),
        job_id=f"qualification_chase_immediate_{lead_id}",
    )
    
    # Enqueue follow-up in 4 hours
    queue.enqueue_in(
        timedelta(hours=4),
        send_missing_info_sms,
        str(lead_id),
        job_id=f"qualification_chase_followup_{lead_id}",
    )
