import os
import uuid
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.guest import Guest
from app.models.noc_application import NOCApplication
from .schema import DocumentUploadResponse

from app.features.noc_application.nicop_service import process_nicop_front_improved, process_nicop_back_improved
from app.features.noc_application.passport_service import process_passport_front
from app.features.noc_application.iqama_service import process_iqama_front

def handle_temp_document_upload(guest_id: UUID, file: UploadFile, doc_type: str, db: Session) -> DocumentUploadResponse:
    
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    noc_app = db.query(NOCApplication).filter(NOCApplication.guest_id == guest_id).first()
    if not noc_app:
        noc_app = NOCApplication(
            guest_id=guest_id,
            status="pending",
            documents_uploaded=True
        )
        db.add(noc_app)
        db.commit()
        db.refresh(noc_app)
        
        guest.tracking_number = noc_app.tracking_number
        db.commit()
    else:
        noc_app.documents_uploaded = True
        db.commit()
    
    upload_dir = os.path.join("uploads", "pending", str(guest_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    file_name = f"{doc_type}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, file_name)
    
    try:
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return DocumentUploadResponse(
        tracking_number=noc_app.tracking_number,
        document_type=doc_type,
        status="uploaded_successfully",
        file_path=file_path,
        message=f"{doc_type.title()} document uploaded successfully"
    )

def process_uploaded_document(guest_id: UUID, doc_type: str, db: Session) -> Dict[str, Any]:
    
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    noc_app = db.query(NOCApplication).filter(NOCApplication.guest_id == guest_id).first()
    if not noc_app:
        raise HTTPException(status_code=404, detail="No NOC application found for this guest")
    
    upload_dir = os.path.join("uploads", "pending", str(guest_id))
    if not os.path.exists(upload_dir):
        raise HTTPException(status_code=404, detail="No uploaded documents found")
    
    files = [f for f in os.listdir(upload_dir) if f.startswith(f"{doc_type}_")]
    if not files:
        raise HTTPException(status_code=404, detail=f"No {doc_type} document found")
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(upload_dir, f)))
    file_path = os.path.join(upload_dir, latest_file)
    
    output_dir = os.path.join("uploads", "processed", str(guest_id))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{doc_type}_processed.jpg")
    
    try:
        if doc_type == "nicop_front":
            result = process_nicop_front_improved(file_path, output_path)
        elif doc_type == "nicop_back":
            result = process_nicop_back_improved(file_path, output_path)
        elif doc_type == "passport":
            result = process_passport_front(file_path, output_path)
        elif doc_type == "iqama":
            result = process_iqama_front(file_path, output_path)
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        if not result:
            raise HTTPException(status_code=422, detail=f"Could not extract data from {doc_type}")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

def get_noc_application_status(guest_id: UUID, db: Session) -> Dict[str, Any]:    
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    noc_app = db.query(NOCApplication).filter(NOCApplication.guest_id == guest_id).first()
    
    if not noc_app:
        return {
            "guest_id": guest_id,
            "tracking_number": None,
            "status": "not_started",
            "documents_uploaded": False,
            "uploaded_documents": []
        }
    
    upload_dir = os.path.join("uploads", "pending", str(guest_id))
    uploaded_docs = []
    
    if os.path.exists(upload_dir):
        for doc_type in ["iqama", "passport", "nicop_front", "nicop_back"]:
            files = [f for f in os.listdir(upload_dir) if f.startswith(f"{doc_type}_")]
            if files:
                uploaded_docs.append(doc_type)
    
    return {
        "guest_id": guest_id,
        "tracking_number": noc_app.tracking_number,
        "status": noc_app.status,
        "burial_location": getattr(noc_app, 'burial_location', None),
        "documents_uploaded": noc_app.documents_uploaded,
        "uploaded_documents": uploaded_docs,
    }

def extract_nicop_front(image_path: str, output_path: str = None):
    return process_nicop_front_improved(image_path, output_path)

def extract_nicop_back(image_path: str, output_path: str = None):
    return process_nicop_back_improved(image_path, output_path)

def extract_passport_front(image_path: str, output_path: str = None):
    return process_passport_front(image_path, output_path)

def extract_iqama_front(image_path: str, output_path: str = None):
    return process_iqama_front(image_path, output_path)