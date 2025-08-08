from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.utils.dependencies import DbSession
from .service import handle_temp_document_upload, process_uploaded_document
from .schema import (
    DocumentUploadResponse, 
    NICOPFrontOCRResponse, 
    NICOPBackOCRResponse, 
    PassportOCRResponse, 
    IqamaOCRResponse
)

router = APIRouter(prefix="/noc", tags=["NOC Application"])

@router.post("/upload/{doc_type}", response_model=DocumentUploadResponse)
def upload_document(
    guest_id: UUID, 
    doc_type: str,
    file: UploadFile = File(...), 
    db: DbSession
):
    valid_types = ["iqama", "passport", "nicop_front", "nicop_back"]
    if doc_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid document type. Valid types: {', '.join(valid_types)}"
        )
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
    
    return handle_temp_document_upload(guest_id, file, doc_type, db)

@router.post("/process-ocr/{doc_type}")
def process_document_ocr(
    guest_id: UUID,
    doc_type: str,
    db: DbSession
):
    valid_types = ["iqama", "passport", "nicop_front", "nicop_back"]
    if doc_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid document type. Valid types: {', '.join(valid_types)}"
        )
    
    return process_uploaded_document(guest_id, doc_type, db)

@router.post("/ocr/nicop/front", response_model=NICOPFrontOCRResponse)
def get_nicop_front_data(guest_id: UUID, db: DbSession):
    return process_uploaded_document(guest_id, "nicop_front", db)

@router.post("/ocr/nicop/back", response_model=NICOPBackOCRResponse)
def get_nicop_back_data(guest_id: UUID, db: DbSession):
    return process_uploaded_document(guest_id, "nicop_back", db)

@router.post("/ocr/passport", response_model=PassportOCRResponse)
def get_passport_data(guest_id: UUID, db: DbSession):
    return process_uploaded_document(guest_id, "passport", db)

@router.post("/ocr/iqama", response_model=IqamaOCRResponse)
def get_iqama_data(guest_id: UUID, db: DbSession):
    return process_uploaded_document(guest_id, "iqama", db)

@router.get("/status/{guest_id}")
def get_noc_status(guest_id: UUID, db: DbSession):
    from .service import get_noc_application_status
    return get_noc_application_status(guest_id, db)