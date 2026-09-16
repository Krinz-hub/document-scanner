"""SQLAlchemy models for border screening lifecycle, documents, and evidence."""

import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Date,
    Float,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class Screening(Base):
    __tablename__ = "screenings"

    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    checkpoint_id = Column(String(64), default="CP-DEFAULT", nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)  # PENDING, PROCESSING, REVIEW_REQUIRED, COMPLETED
    review_priority = Column(String(16), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH

    # Relationships
    documents = relationship("DocumentRecord", back_populates="screening", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="screening", cascade="all, delete-orphan")
    validation_results = relationship("ValidationResult", back_populates="screening", cascade="all, delete-orphan")
    tampering_results = relationship("TamperingResult", back_populates="screening", cascade="all, delete-orphan")
    face_results = relationship("FaceResult", back_populates="screening", cascade="all, delete-orphan")
    external_checks = relationship("ExternalCheck", back_populates="screening", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItem", back_populates="screening", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="screening", cascade="all, delete-orphan")


class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(32), nullable=True)  # PASSPORT, NATIONAL_ID, VISA, PERMIT
    document_number_hash = Column(String(128), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    object_reference = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    screening = relationship("Screening", back_populates="documents")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(64), nullable=False)
    value_text = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    source = Column(String(32), default="OCR")  # OCR, MRZ, BARCODE

    screening = relationship("Screening", back_populates="extracted_fields")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    check_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)  # PASS, FAIL, REVIEW
    evidence = Column(JSON, nullable=True)
    ruleset_version = Column(String(32), default="v1.0")

    screening = relationship("Screening", back_populates="validation_results")


class TamperingResult(Base):
    __tablename__ = "tampering_results"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    region = Column(String(64), nullable=False)  # PHOTO, TEXT, STAMP, BACKGROUND
    detector = Column(String(64), nullable=False)  # OPENCV_BASELINE, NOISE_ANALYSIS
    status = Column(String(32), nullable=False)  # CLEAN, SUSPICIOUS, INSUFFICIENT_EVIDENCE
    confidence = Column(Float, default=0.0)
    evidence = Column(JSON, nullable=True)
    model_version = Column(String(32), default="tamper-baseline-v1")

    screening = relationship("Screening", back_populates="tampering_results")


class FaceResult(Base):
    __tablename__ = "face_results"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    similarity = Column(Float, nullable=True)
    quality = Column(Float, nullable=True)
    status = Column(String(32), nullable=False)  # MATCH, REVIEW, LOW_SIMILARITY, NO_FACE_DETECTED
    model_version = Column(String(32), default="face-compare-v1")

    screening = relationship("Screening", back_populates="face_results")


class ExternalCheck(Base):
    __tablename__ = "external_checks"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(64), nullable=False)  # MOCK_REGISTRY, GOV_API
    status = Column(String(32), nullable=False)  # VALID, EXPIRED, REVOKED, NOT_FOUND, UNAVAILABLE
    response_reference = Column(String(256), nullable=True)
    checked_at = Column(DateTime, default=utc_now)

    screening = relationship("Screening", back_populates="external_checks")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(64), nullable=False)  # RULE_MISMATCH, TAMPERING, FACE, REGISTRY
    severity = Column(String(16), nullable=False)  # INFO, WARNING, CRITICAL
    explanation = Column(Text, nullable=False)
    source_module = Column(String(64), nullable=False)

    screening = relationship("Screening", back_populates="evidence_items")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(64), primary_key=True, index=True)
    screening_id = Column(String(64), ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(64), nullable=False)  # CREATED, DOCUMENT_UPLOADED, REVIEW_UPDATED
    timestamp = Column(DateTime, default=utc_now)
    actor = Column(String(64), default="system")
    event_metadata = Column(JSON, nullable=True)

    screening = relationship("Screening", back_populates="audit_events")
