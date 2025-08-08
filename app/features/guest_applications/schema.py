from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional
from uuid import UUID


class GuestBase(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None


class GuestCreate(GuestBase):
    pass


class GuestOut(GuestBase):
    id: UUID  
    full_name: str
    phone_number: str
    email: Optional[EmailStr]
    ip_address: Optional[str]
    tracking_number: Optional[UUID]

    class Config:
        from_attributes = True 