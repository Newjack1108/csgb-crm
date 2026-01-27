from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime
from typing import Optional

from app.modules.leads.models import IdempotencyKey


def check_idempotency_key(db: Session, key: str) -> tuple[bool, Optional[IdempotencyKey]]:
    """
    Check if an idempotency key exists.
    Returns (exists, key_record)
    """
    stmt = select(IdempotencyKey).where(IdempotencyKey.key == key)
    result = db.execute(stmt).scalar_one_or_none()
    return result is not None, result


def create_idempotency_key(db: Session, key: str) -> IdempotencyKey:
    """Create a new idempotency key"""
    idempotency_key = IdempotencyKey(id=uuid4(), key=key, created_at=datetime.utcnow())
    db.add(idempotency_key)
    db.commit()
    db.refresh(idempotency_key)
    return idempotency_key


def generate_idempotency_key(source: str, external_id: Optional[str] = None, payload_hash: Optional[str] = None) -> str:
    """
    Generate an idempotency key from source and external_id or payload hash.
    """
    if external_id:
        return f"{source}:{external_id}"
    elif payload_hash:
        return f"{source}:hash:{payload_hash}"
    else:
        return f"{source}:{uuid4().hex}"
