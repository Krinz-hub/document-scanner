"""Screening lifecycle API endpoints."""

import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.screening import Screening, AuditEvent
from backend.app.schemas.screening import (
    ScreeningCreate,
    ScreeningDecision,
    ScreeningSummary,
    ScreeningDetail,
    EvidenceItemSchema,
)

router = APIRouter()


@router.post(
    "/screenings/{screening_id}/decision",
    response_model=ScreeningDetail,
    summary="Record officer manual inspection decision",
)
def record_officer_decision(
    screening_id: str,
    payload: ScreeningDecision,
    db: Session = Depends(get_db),
):
    screening = db.query(Screening).filter_by(id=screening_id).first()
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Screening '{screening_id}' not found")

    action_map = {
        "ACCEPTED": "ACCEPTED",
        "CLEAR": "ACCEPTED",
        "REJECTED": "REJECTED",
        "REJECT": "REJECTED",
        "ESCALATED": "ESCALATED",
        "REFER_SECONDARY": "ESCALATED",
    }
    action_raw = payload.action.upper()
    if action_raw not in action_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{payload.action}'. Allowed actions: {', '.join(action_map.keys())}",
        )

    officer_id = payload.decided_by or payload.officer_id or "OFFICER-01"
    now = datetime.now(timezone.utc)
    screening.status = action_map[action_raw]
    screening.officer_action = action_raw
    screening.officer_notes = payload.notes
    screening.decided_at = now
    screening.decided_by = officer_id

    # Append immutable audit event
    audit = AuditEvent(
        id=uuid.uuid4().hex,
        screening_id=screening_id,
        event_type="OFFICER_DECISION_RECORDED",
        actor=officer_id,
        event_metadata={"action": action_raw, "status": screening.status, "notes": payload.notes},
    )
    db.add(audit)
    db.commit()
    db.refresh(screening)

    return build_screening_detail(screening)


@router.get(
    "/screenings/{screening_id}/audit",
    summary="Get immutable audit trail of screening events",
)
def get_screening_audit_trail(
    screening_id: str,
    db: Session = Depends(get_db),
):
    screening = db.query(Screening).filter_by(id=screening_id).first()
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Screening '{screening_id}' not found")

    events = db.query(AuditEvent).filter_by(screening_id=screening_id).order_by(AuditEvent.timestamp.asc()).all()
    return [
        {
            "id": e.id,
            "screening_id": e.screening_id,
            "event_type": e.event_type,
            "timestamp": e.timestamp,
            "actor": e.actor,
            "metadata": e.event_metadata,
        }
        for e in events
    ]


def generate_screening_id() -> str:
    """Generate human-readable and unique screening identifier."""
    now = datetime.now(timezone.utc)
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"SCR-{now.strftime('%Y%m%d')}-{short_uuid}"


@router.post(
    "/screenings",
    response_model=ScreeningDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new screening session",
)
def create_screening(
    payload: ScreeningCreate = ScreeningCreate(),
    db: Session = Depends(get_db),
):
    screening_id = generate_screening_id()
    new_screening = Screening(
        id=screening_id,
        checkpoint_id=payload.checkpoint_id or "CP-01",
        status="PENDING",
        review_priority="LOW",
    )
    audit = AuditEvent(
        id=uuid.uuid4().hex,
        screening_id=screening_id,
        event_type="SCREENING_INITIALIZED",
        actor="officer_workstation",
        event_metadata={"checkpoint": payload.checkpoint_id},
    )

    db.add(new_screening)
    db.add(audit)
    db.commit()
    db.refresh(new_screening)

    return build_screening_detail(new_screening)


@router.get(
    "/screenings",
    response_model=List[ScreeningSummary],
    summary="List screening sessions",
)
def list_screenings(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    screenings = (
        db.query(Screening)
        .order_by(desc(Screening.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return screenings


@router.get(
    "/screenings/{screening_id}",
    response_model=ScreeningDetail,
    summary="Get screening session details",
)
def get_screening(
    screening_id: str,
    db: Session = Depends(get_db),
):
    screening = db.query(Screening).filter_by(id=screening_id).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening '{screening_id}' not found",
        )
    return build_screening_detail(screening)


@router.get(
    "/screenings/{screening_id}/evidence",
    response_model=List[EvidenceItemSchema],
    summary="Get normalized screening evidence",
)
def get_screening_evidence(
    screening_id: str,
    db: Session = Depends(get_db),
):
    screening = db.query(Screening).filter_by(id=screening_id).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening '{screening_id}' not found",
        )
    return screening.evidence_items


def build_screening_detail(screening: Screening) -> ScreeningDetail:
    """Helper to aggregate module states and human-readable reasons."""
    reasons = [e.explanation for e in screening.evidence_items if e.severity in ("WARNING", "CRITICAL")]

    # Verification state mapping
    verification = {
        "mrz": "PENDING",
        "external": "PENDING",
        "face": "PENDING",
    }
    for val in screening.validation_results:
        if "mrz" in val.check_name.lower():
            verification["mrz"] = val.status

    for ext in screening.external_checks:
        verification["external"] = ext.status

    for face in screening.face_results:
        verification["face"] = face.status

    # Analysis state mapping
    analysis = {
        "photo": "PENDING",
        "text": "PENDING",
        "stamp": "PENDING",
    }
    for t in screening.tampering_results:
        region = t.region.lower()
        if region in analysis:
            analysis[region] = t.status

    return ScreeningDetail(
        id=screening.id,
        checkpoint_id=screening.checkpoint_id,
        status=screening.status,
        review_priority=screening.review_priority,
        created_at=screening.created_at,
        updated_at=screening.updated_at,
        officer_action=screening.officer_action,
        officer_notes=screening.officer_notes,
        decided_at=screening.decided_at,
        decided_by=screening.decided_by,
        documents=screening.documents,
        extracted_fields=screening.extracted_fields,
        evidence_items=screening.evidence_items,
        reasons=reasons,
        verification=verification,
        analysis=analysis,
    )
