from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.guest import Guest
from app.models.noc_application import NOCApplication
from .schema import CreateGuestRequest, GuestCreate
from sqlalchemy import or_, and_


def create_guest(db: Session, payload: CreateGuestRequest) -> Guest:
    filters = [Guest.phone_number == payload.phone_number]
    if payload.email:
        filters.append(Guest.email == payload.email)

    existing_guest = db.query(Guest).filter(or_(*filters)).first()
    if existing_guest:
        raise HTTPException(
            status_code=409,
            detail="Guest with this phone number or email already exists",
        )

    guest = Guest(
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        email=payload.email,
        nationality=payload.nationality,
    )

    db.add(guest)
    db.commit()
    db.refresh(guest)

    return guest


def get_guest_by_id(db: Session, guest_id: UUID):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest


def get_all_guests(db: Session):
    return db.query(Guest).all()


def delete_guest_by_tracking_number(db: Session, tracking_number: UUID):
    noc_app = (
        db.query(NOCApplication)
        .filter(NOCApplication.tracking_number == tracking_number)
        .first()
    )

    if not noc_app:
        raise HTTPException(
            status_code=404, detail="NOCApplication with this tracking number not found"
        )

    guest = noc_app.guest
    if not guest:
        raise HTTPException(
            status_code=404, detail="Guest not found for this tracking number"
        )
    db.delete(guest)
    db.commit()

    return {"message": f"Guest with tracking number {tracking_number} deleted"}
