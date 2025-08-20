from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class ServiceTypeResponse(BaseModel):
    id: UUID
    name: str
    description: str
    active: Optional[bool] = True

    class Config:
        from_attributes = True
