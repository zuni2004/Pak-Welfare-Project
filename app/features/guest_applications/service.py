from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.guest import Guest
from app.models.noc_application import NOCApplication
from .schema import GuestCreate


def create_guest_application(db: Session, payload: GuestCreate, ip_address: str) -> Guest:
    guest = Guest(
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        email=payload.email,
        ip_address=ip_address,
        tracking_number=None
    )

    db.add(guest)
    db.commit()
    db.refresh(guest)
    
    return guest


def get_guest_by_id(db: Session, guest_id):
    guest = db.query(Guest).filter(Guest.guest_id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest


def get_all_guests(db: Session):
    return db.query(Guest).all()


def delete_guest_application(db: Session, guest_id):
    guest = get_guest_by_id(db, guest_id)
    db.delete(guest)
    db.commit()
    return {"message": "Guest deleted"}
