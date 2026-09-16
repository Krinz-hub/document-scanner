"""Screening Orchestrator coordinating all validation and perception modules."""

import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.screening import (
    Screening,
    DocumentRecord,
    ExtractedField,
    ValidationResult,
    TamperingResult,
    FaceResult,
    ExternalCheck,
    EvidenceItem,
    AuditEvent,
)
from backend.app.modules.quality import quality_assessor
from backend.app.modules.ocr import ocr_engine
from backend.app.modules.mrz import mrz_validator
from backend.app.modules.rules import rules_engine
from backend.app.modules.tampering import tampering_detector
from backend.app.modules.face import face_engine
from backend.app.modules.external import get_external_provider
from backend.app.storage import storage_manager


class ScreeningOrchestrator:
    def process_document(
        self,
        screening_id: str,
        file_bytes: bytes,
        filename: str,
        db: Session,
        raw_mrz_line1: Optional[str] = None,
        raw_mrz_line2: Optional[str] = None,
        raw_text_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute the document intake, quality check, OCR, MRZ, rules, and tampering pipeline."""
        screening = db.query(Screening).filter_by(id=screening_id).first()
        if not screening:
            raise ValueError(f"Screening '{screening_id}' does not exist")

        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        object_key = f"documents/{screening_id}/{doc_id}_{filename}"

        # 1. Image Quality Assessment
        quality_res = quality_assessor.assess_bytes(file_bytes)
        if quality_res["status"] == "LOW_IMAGE_QUALITY":
            for issue in quality_res["issues"]:
                db.add(EvidenceItem(
                    id=uuid.uuid4().hex,
                    screening_id=screening_id,
                    category="IMAGE_QUALITY",
                    severity="WARNING",
                    explanation=issue,
                    source_module="quality_assessor",
                ))

        # 2. Store document file securely
        object_ref = storage_manager.save_file(file_bytes, object_key)
        doc_record = DocumentRecord(
            id=doc_id,
            screening_id=screening_id,
            type="PASSPORT",
            object_reference=object_ref,
        )
        db.add(doc_record)

        # 3. OCR Text and Field Extraction
        text_source = raw_text_hint or ""
        extracted_fields = ocr_engine.parse_fields_from_text(text_source)

        canonical_data = {}
        for fname, fval in extracted_fields.items():
            canonical_data[fname] = fval["value"]
            db.add(ExtractedField(
                id=uuid.uuid4().hex,
                screening_id=screening_id,
                field_name=fname,
                value_text=str(fval["value"]),
                confidence=fval["confidence"],
                source=fval["source"],
            ))

        # 4. MRZ Extraction & Validation (if available)
        mrz_data = None
        if raw_mrz_line1 and raw_mrz_line2:
            try:
                mrz_data = mrz_validator.parse_td3(raw_mrz_line1, raw_mrz_line2)

                # Cross-compare with visual OCR
                mismatches = mrz_validator.compare_with_visual(mrz_data, extracted_fields)
                for mm in mismatches:
                    db.add(EvidenceItem(
                        id=uuid.uuid4().hex,
                        screening_id=screening_id,
                        category="CROSS_FIELD_MISMATCH",
                        severity="CRITICAL",
                        explanation=mm["explanation"],
                        source_module="mrz_validator",
                    ))

                # Store MRZ ValidationResult
                mrz_status = "PASS" if mrz_data["checksums"]["all_valid"] and not mismatches else "FAIL"
                db.add(ValidationResult(
                    id=uuid.uuid4().hex,
                    screening_id=screening_id,
                    check_name="MRZ_CHECKSUM_VALIDATION",
                    status=mrz_status,
                    evidence=mrz_data["checksums"],
                    ruleset_version="icao-9303-td3",
                ))

                if not mrz_data["checksums"]["all_valid"]:
                    db.add(EvidenceItem(
                        id=uuid.uuid4().hex,
                        screening_id=screening_id,
                        category="MRZ_CHECKSUM",
                        severity="CRITICAL",
                        explanation="MRZ check-digit verification failed",
                        source_module="mrz_validator",
                    ))

                # Fill in missing canonical data from MRZ and persist to ExtractedField
                for k in ("document_number", "nationality", "date_of_birth", "expiry_date"):
                    if not canonical_data.get(k) and mrz_data.get(k):
                        canonical_data[k] = mrz_data[k]
                        db.add(ExtractedField(
                            id=uuid.uuid4().hex,
                            screening_id=screening_id,
                            field_name=k,
                            value_text=str(mrz_data[k]),
                            confidence=0.99,
                            source="MRZ",
                        ))
                if not canonical_data.get("name") and mrz_data.get("full_name"):
                    canonical_data["name"] = mrz_data["full_name"]
                    db.add(ExtractedField(
                        id=uuid.uuid4().hex,
                        screening_id=screening_id,
                        field_name="name",
                        value_text=mrz_data["full_name"],
                        confidence=0.99,
                        source="MRZ",
                    ))

            except Exception as e:
                db.add(ValidationResult(
                    id=uuid.uuid4().hex,
                    screening_id=screening_id,
                    check_name="MRZ_CHECKSUM_VALIDATION",
                    status="FAIL",
                    evidence={"error": str(e)},
                    ruleset_version="icao-9303-td3",
                ))

        # 5. Deterministic Rule Validation
        rule_res = rules_engine.evaluate(canonical_data)
        for vr in rule_res["validation_results"]:
            db.add(ValidationResult(
                id=uuid.uuid4().hex,
                screening_id=screening_id,
                check_name=vr["check_name"],
                status=vr["status"],
                evidence=vr["evidence"],
                ruleset_version=vr["ruleset_version"],
            ))
        for ev in rule_res["evidence_items"]:
            db.add(EvidenceItem(
                id=uuid.uuid4().hex,
                screening_id=screening_id,
                category=ev["category"],
                severity=ev["severity"],
                explanation=ev["explanation"],
                source_module=ev["source_module"],
            ))

        # 6. Tampering Analysis
        tamper_res = tampering_detector.analyze_bytes(file_bytes)
        for tr in tamper_res["results"]:
            db.add(TamperingResult(
                id=uuid.uuid4().hex,
                screening_id=screening_id,
                region=tr["region"],
                detector=tr["detector"],
                status=tr["status"],
                confidence=tr["confidence"],
                evidence=tr["evidence"],
                model_version=tr["model_version"],
            ))
        for ev in tamper_res["evidence_items"]:
            db.add(EvidenceItem(
                id=uuid.uuid4().hex,
                screening_id=screening_id,
                category=ev["category"],
                severity=ev["severity"],
                explanation=ev["explanation"],
                source_module=ev["source_module"],
            ))

        # 7. External Registry Verification Check
        ext_provider = get_external_provider()
        doc_num = canonical_data.get("document_number", "")
        nat = canonical_data.get("nationality", "UTO")
        ext_res = ext_provider.verify_document(doc_num, nat, "PASSPORT")

        db.add(ExternalCheck(
            id=uuid.uuid4().hex,
            screening_id=screening_id,
            provider=ext_res["provider"],
            status=ext_res["status"],
            response_reference=ext_res.get("registry_record_id"),
        ))

        if ext_res["status"] in ("REVOKED", "EXPIRED", "NOT_FOUND"):
            db.add(EvidenceItem(
                id=uuid.uuid4().hex,
                screening_id=screening_id,
                category="EXTERNAL_REGISTRY",
                severity="CRITICAL",
                explanation=f"Registry alert: {ext_res['reason']}",
                source_module="external_registry",
            ))

        # 8. Compute Explainable Review Priority
        self._update_screening_status_and_priority(screening, db)

        db.add(AuditEvent(
            id=uuid.uuid4().hex,
            screening_id=screening_id,
            event_type="DOCUMENT_PROCESSED",
            actor="screening_orchestrator",
            event_metadata={"doc_id": doc_id, "quality_score": quality_res["score"]},
        ))
        db.commit()

        return {
            "document_id": doc_id,
            "object_reference": object_ref,
            "quality": quality_res,
            "extracted_fields": canonical_data,
            "mrz": mrz_data,
            "rules_status": rule_res["overall_status"],
            "tampering_status": tamper_res["overall_status"],
            "external_status": ext_res["status"],
        }

    def process_face(
        self,
        screening_id: str,
        live_face_bytes: bytes,
        db: Session,
    ) -> Dict[str, Any]:
        """Verify traveler live face capture against the uploaded document portrait."""
        screening = db.query(Screening).filter_by(id=screening_id).first()
        if not screening:
            raise ValueError(f"Screening '{screening_id}' not found")

        doc = db.query(DocumentRecord).filter_by(screening_id=screening_id).first()
        if not doc or not doc.object_reference:
            raise ValueError("No document portrait found for this screening session")

        # Load document image
        doc_bytes = storage_manager.get_file(doc.object_reference)

        # Run Face Verification Engine
        face_res = face_engine.compare_faces(doc_bytes, live_face_bytes)

        db.add(FaceResult(
            id=uuid.uuid4().hex,
            screening_id=screening_id,
            similarity=face_res["similarity"],
            quality=face_res["quality"],
            status=face_res["status"],
            model_version=face_res["model_version"],
        ))

        if face_res["status"] in ("LOW_SIMILARITY", "REVIEW", "NO_FACE_DETECTED"):
            severity = "CRITICAL" if face_res["status"] == "LOW_SIMILARITY" else "WARNING"
            db.add(EvidenceItem(
                id=uuid.uuid4().hex,
                screening_id=screening_id,
                category="FACE_VERIFICATION",
                severity=severity,
                explanation=face_res["explanation"],
                source_module="face_engine",
            ))

        self._update_screening_status_and_priority(screening, db)

        db.add(AuditEvent(
            id=uuid.uuid4().hex,
            screening_id=screening_id,
            event_type="FACE_VERIFIED",
            actor="screening_orchestrator",
            event_metadata={"status": face_res["status"], "similarity": face_res["similarity"]},
        ))
        db.commit()

        return face_res

    def _update_screening_status_and_priority(self, screening: Screening, db: Session):
        """Explainable review priority: LOW / MEDIUM / HIGH."""
        db.flush()
        # Query active critical or warning evidence
        evidence = db.query(EvidenceItem).filter_by(screening_id=screening.id).all()
        critical_count = sum(1 for e in evidence if e.severity == "CRITICAL")
        warning_count = sum(1 for e in evidence if e.severity == "WARNING")

        if critical_count > 0:
            screening.review_priority = "HIGH"
            screening.status = "REVIEW_REQUIRED"
        elif warning_count > 0:
            screening.review_priority = "MEDIUM"
            screening.status = "REVIEW_REQUIRED"
        else:
            screening.review_priority = "LOW"
            screening.status = "COMPLETED"


orchestrator = ScreeningOrchestrator()
