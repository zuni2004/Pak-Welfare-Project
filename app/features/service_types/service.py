from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.service_type import ServiceType
from .schema import ServiceTypeCreate, ServiceTypeUpdate
import uuid
from slugify import slugify  

def create_service_type(db: Session, data: ServiceTypeCreate) -> ServiceType:
    service_data = data.dict()
    if not service_data.get("slug"):
        service_data["slug"] = slugify(service_data["name"])
    service = ServiceType(**service_data)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def get_service_types(db: Session):
    return db.query(ServiceType).all()

def get_service_type_by_id(db: Session, id: uuid.UUID):
    return db.query(ServiceType).filter(ServiceType.id == id).first()

def update_service_type(db: Session, id: uuid.UUID, data: ServiceTypeUpdate):
    service = get_service_type_by_id(db, id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if "name" in update_data and not update_data.get("slug"):
        update_data["slug"] = slugify(update_data["name"])
    for field, value in data.dict(exclude_unset=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service