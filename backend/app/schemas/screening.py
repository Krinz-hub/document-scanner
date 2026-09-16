"""Pydantic schemas for screening API request and responses."""

from datetime import datetime, date
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


class ScreeningCreate(BaseModel):
    checkpoint_id: Optional[str] = "CP-01"


class DocumentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    screening_id: str
    type: Optional[str] = None
    document_number_hash: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    object_reference: Optional[str] = None
    created_at: datetime


class ExtractedFieldSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    field_name: str
    value_text: Optional[str] = None
    confidence: float
    source: str


class EvidenceItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    severity: str
    explanation: str
    source_module: str


class ScreeningSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    checkpoint_id: str
    status: str
    review_priority: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ScreeningDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    checkpoint_id: str
    status: str
    review_priority: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    documents: List[DocumentSchema] = []
    extracted_fields: List[ExtractedFieldSchema] = []
    evidence_items: List[EvidenceItemSchema] = []
    reasons: List[str] = []
    verification: Dict[str, str] = {
        "mrz": "PENDING",
        "external": "PENDING",
        "face": "PENDING"
    }
    analysis: Dict[str, str] = {
        "photo": "PENDING",
        "text": "PENDING",
        "stamp": "PENDING"
    }
