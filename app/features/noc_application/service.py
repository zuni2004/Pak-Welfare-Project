import os
from fastapi import UploadFile, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.noc_application import NOCApplication
from app.models.guest import Guest

UPLOAD_DIR = "uploads/documents"

def handle_temp_document_upload(guest_id: UUID, file: UploadFile, doc_type: str, db: Session):
    guest = db.query(Guest).filter_by(guest_id=guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    folder = os.path.join("uploads", "pending", str(guest_id))
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{doc_type}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return {
        "guest_id": guest_id,
        "document_type": doc_type,
        "status": "uploaded"
    }
