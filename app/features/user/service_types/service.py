from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .schema import ServiceTypeResponse
from app.models import ServiceType
from uuid import UUID


def get_service_types(db: Session) -> List[ServiceTypeResponse]:
    return db.query(ServiceType).all()


def get_service_type_by_id(db: Session, id: UUID) -> ServiceTypeResponse:
    service = db.query(ServiceType).filter(ServiceType.id == id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
