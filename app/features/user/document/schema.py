from typing import Optional, List
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    document_type: str
    document_url: str
    message: str


class SmartDocumentUploadResponse(BaseModel):
    uploaded_documents: List[DocumentUploadResponse]
    nationality: str
    user_type: str
    user_id: Optional[str] = None
    guest_id: Optional[str] = None
    total_documents: int
    message: str
