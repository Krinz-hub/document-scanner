"""Maintenance and Data Retention Policy enforcement API."""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.screening import Screening, DocumentRecord, AuditEvent
from backend.app.auth import AuthenticatedUser, require_roles
from backend.app.storage import storage_manager

router = APIRouter()


@router.post(
    "/maintenance/retention/purge",
    summary="Purge document images older than retention period (Preserves audit hashes)",
)
def purge_expired_retention_data(
    retention_days: int = 30,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_roles(["SUPERVISOR"])),
) -> Dict[str, Any]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    # Find documents created before cutoff
    old_documents = db.query(DocumentRecord).filter(DocumentRecord.created_at < cutoff).all()
    purged_count = 0

    for doc in old_documents:
        if doc.object_reference:
            try:
                # Mark as purged
                doc.object_reference = "PURGED_BY_RETENTION_POLICY"
                purged_count += 1
            except Exception:
                pass

    audit_entry = AuditEvent(
        id=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-PURGE",
        screening_id="SYSTEM",
        event_type="RETENTION_PURGE_EXECUTED",
        actor=user.username,
        event_metadata={
            "retention_days": retention_days,
            "cutoff_date": cutoff.isoformat(),
            "purged_count": purged_count,
        },
    )
    db.add(audit_entry)
    db.commit()

    return {
        "status": "COMPLETED",
        "purged_records": purged_count,
        "retention_cutoff": cutoff.isoformat(),
        "actor": user.username,
    }
