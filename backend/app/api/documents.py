"""Document upload, preview, and live biometric capture API."""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Response
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.screening import Screening, DocumentRecord
from backend.app.modules.orchestrator import orchestrator
from backend.app.modules.quality import quality_assessor
from backend.app.storage import storage_manager

router = APIRouter()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB


@router.post("/screenings/{screening_id}/document", summary="Upload and process document")
async def upload_document(
    screening_id: str,
    file: UploadFile = File(...),
    mrz_line1: Optional[str] = Form(None),
    mrz_line2: Optional[str] = Form(None),
    text_hint: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # 1. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # 2. Read bytes and validate size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    try:
        result = orchestrator.process_document(
            screening_id=screening_id,
            file_bytes=file_bytes,
            filename=file.filename or "document.jpg",
            db=db,
            raw_mrz_line1=mrz_line1,
            raw_mrz_line2=mrz_line2,
            raw_text_hint=text_hint,
        )
        return {
            "status": "PROCESSED",
            "screening_id": screening_id,
            "document": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Processing error: {str(e)}")


@router.post("/screenings/{screening_id}/face", summary="Submit live face capture")
async def submit_live_face(
    screening_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    try:
        result = orchestrator.process_face(
            screening_id=screening_id,
            live_face_bytes=file_bytes,
            db=db,
        )
        return {
            "status": "PROCESSED",
            "screening_id": screening_id,
            "face_result": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/screenings/{screening_id}/document/image", summary="Stream document image preview")
def get_document_image(
    screening_id: str,
    db: Session = Depends(get_db),
):
    doc = db.query(DocumentRecord).filter_by(screening_id=screening_id).first()
    if not doc or not doc.object_reference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No document found for screening")

    try:
        img_bytes = storage_manager.get_file(doc.object_reference)
        return Response(content=img_bytes, media_type="image/jpeg")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored document file missing")


@router.post("/quality/assess", summary="Standalone document image quality assessment")
async def assess_image_quality(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")

    file_bytes = await file.read()
    return quality_assessor.assess_bytes(file_bytes)
