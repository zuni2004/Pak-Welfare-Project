from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class UploadResponse(BaseModel):
    filename: str
    message: str
    

class NICOPFrontResponse(BaseModel):
    name: str
    father_name: str
    gender: str
    country: str
    cnic_number: str
    date_of_birth: str
    date_of_issue: str
    date_of_expiry: str


class NICOPBackResponse(BaseModel):
    present_address: str
    permanent_address: str
    raw_text: List[str]


class OCRResponse(BaseModel):
    message: str
    data: Dict[str, Any]

class PassportRequest(BaseModel):
    image_path: str

class PassportResponse(BaseModel):
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
    
class IqamaData(BaseModel):
    english_name: Optional[str]
    iqama_number_arabic: Optional[str]
    iqama_number_english: Optional[str]
    issue_date: Optional[str]
    expiry_date: Optional[str]

class OCRResponse(BaseModel):
    message: str
    data: IqamaData
    cleaned_image_path: Optional[str] = None
    ocr_visualization_path: Optional[str] = None
    text_output_path: Optional[str] = None
    structured_output_path: Optional[str] = None