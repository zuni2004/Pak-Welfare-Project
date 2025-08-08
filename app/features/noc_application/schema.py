# features/noc_application/schema.py
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    tracking_number: UUID
    document_type: str
    status: str
    file_path: Optional[str] = None  
    message: Optional[str] = None

class NICOPFrontOCRRequest(BaseModel):
    image_path: str
    output_path: Optional[str] = None

class NICOPFrontOCRResponse(BaseModel):
    name: str
    father_name: str
    gender: str
    country: str
    cnic_number: str
    date_of_birth: str
    date_of_issue: str
    date_of_expiry: str

class NICOPBackOCRRequest(BaseModel):
    image_path: str
    output_path: Optional[str] = None

class NICOPBackOCRResponse(BaseModel):
    present_address: str
    permanent_address: str

class PassportOCRRequest(BaseModel):
    image_path: str
    output_path: Optional[str] = None

class PassportOCRResponse(BaseModel):
    type: str
    country_code: str
    passport_number: str
    surname: str
    given_names: str
    nationality: str
    citizenship_number: str
    sex: str
    date_of_birth: str
    place_of_birth: str
    father_name: str
    date_of_issue: str
    date_of_expiry: str
    issuing_authority: str
    tracking_number: str
    booklet_number: str
    mrz_lines: List[str]

class IqamaOCRRequest(BaseModel):
    image_path: str
    output_path: Optional[str] = None

class IqamaOCRResponse(BaseModel):
    english_name: Optional[str]
    iqama_number_arabic: Optional[str]
    iqama_number_english: Optional[str]
    issue_date: Optional[str]
    expiry_date: Optional[str]

class NOCApplicationCreate(BaseModel):
    guest_id: UUID
    burial_location: Optional[str] = None 

class NOCApplicationOut(BaseModel):
    tracking_number: UUID
    guest_id: UUID
    status: str
    burial_location: Optional[str]
    documents_uploaded: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  