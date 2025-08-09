from pydantic import BaseModel, UUID4
from typing import Optional

class ServiceTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class ServiceTypeCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = True

class ServiceTypeUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

class ServiceTypeOut(ServiceTypeBase):
    class Config:
        from_attributes = True

