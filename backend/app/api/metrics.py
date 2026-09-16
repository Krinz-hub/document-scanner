"""Prometheus monitoring metrics endpoint."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.screening import Screening, DocumentRecord, FaceResult

router = APIRouter()


@router.get("/metrics", summary="Prometheus monitoring metrics")
def get_metrics(db: Session = Depends(get_db)):
    total_screenings = db.query(Screening).count()
    review_required = db.query(Screening).filter_by(status="REVIEW_REQUIRED").count()
    accepted = db.query(Screening).filter_by(status="ACCEPTED").count()
    rejected = db.query(Screening).filter_by(status="REJECTED").count()
    total_docs = db.query(DocumentRecord).count()
    total_faces = db.query(FaceResult).count()

    metrics_text = f"""# HELP border_screenings_total Total screening sessions created
# TYPE border_screenings_total counter
border_screenings_total {total_screenings}

# HELP border_screenings_status Screening count by status
# TYPE border_screenings_status gauge
border_screenings_status{{status="REVIEW_REQUIRED"}} {review_required}
border_screenings_status{{status="ACCEPTED"}} {accepted}
border_screenings_status{{status="REJECTED"}} {rejected}

# HELP border_documents_processed_total Total documents ingested
# TYPE border_documents_processed_total counter
border_documents_processed_total {total_docs}

# HELP border_face_verifications_total Total biometric face comparisons
# TYPE border_face_verifications_total counter
border_face_verifications_total {total_faces}

# HELP border_system_healthy Operational health status
# TYPE border_system_healthy gauge
border_system_healthy 1
"""
    return Response(content=metrics_text.strip() + "\n", media_type="text/plain; version=0.0.4")
