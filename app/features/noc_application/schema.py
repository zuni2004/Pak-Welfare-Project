from pydantic import BaseModel, Field
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
    # mrz_lines: List[str]

class IqamaData(BaseModel):
    # english_name: Optional[str] = Field(None, description="Name in English")
    # arabic_name: Optional[str] = Field(None, description="Name in Arabic")
    iqama_number_arabic: Optional[str] = Field(None, description="Iqama number in Arabic digits")