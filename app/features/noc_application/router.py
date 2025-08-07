from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.utils.database import get_db
from .service import handle_temp_document_upload
from .schema import DocumentUploadResponse


router = APIRouter(prefix="/noc", tags=["NOC Application"])

@router.post("/upload/iqama")
def upload_iqama(guest_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return handle_temp_document_upload(guest_id, file, "iqama", db)

@router.post("/upload/passport")
def upload_passport(guest_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return handle_temp_document_upload(guest_id, file, "passport", db)

@router.post("/upload/nicop")
def upload_nicop(guest_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return handle_temp_document_upload(guest_id, file, "nicop", db)
