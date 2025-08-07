from pydantic import BaseModel, UUID4
from typing import Optional

class ServiceTypeBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    active: Optional[bool] = True

class ServiceTypeCreate(ServiceTypeBase):
    pass

class ServiceTypeUpdate(ServiceTypeBase):
    pass

class ServiceTypeOut(ServiceTypeBase):
    id: UUID4

    class Config:
        orm_mode = True
