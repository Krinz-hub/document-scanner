"""Tests for SQLAlchemy database models."""

from backend.app.models.screening import Screening, DocumentRecord, EvidenceItem


def test_create_and_query_screening(db_session):
    screening = Screening(
        id="SCR-TEST-001",
        checkpoint_id="CP-TERMINAL-1",
        status="PENDING",
        review_priority="LOW",
    )
    db_session.add(screening)
    db_session.commit()

    queried = db_session.query(Screening).filter_by(id="SCR-TEST-001").first()
    assert queried is not None
    assert queried.status == "PENDING"
    assert queried.review_priority == "LOW"


def test_screening_cascade_relationships(db_session):
    screening = Screening(id="SCR-TEST-002", status="REVIEW_REQUIRED", review_priority="HIGH")
    doc = DocumentRecord(id="DOC-001", screening_id="SCR-TEST-002", type="PASSPORT")
    evidence = EvidenceItem(
        id="EVD-001",
        screening_id="SCR-TEST-002",
        category="RULE_MISMATCH",
        severity="WARNING",
        explanation="Date of birth discrepancy",
        source_module="rules_engine",
    )
    db_session.add_all([screening, doc, evidence])
    db_session.commit()

    queried = db_session.query(Screening).filter_by(id="SCR-TEST-002").first()
    assert len(queried.documents) == 1
    assert queried.documents[0].type == "PASSPORT"
    assert len(queried.evidence_items) == 1
    assert queried.evidence_items[0].category == "RULE_MISMATCH"
