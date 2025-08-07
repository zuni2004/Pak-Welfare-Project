from pydantic import BaseModel
from uuid import UUID

class DocumentUploadResponse(BaseModel):
    tracking_number: UUID
    document_type: str
    status: str
