from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from uuid import UUID

from .schema import GuestCreate, GuestOut
from .service import (
    create_guest_application,
    get_guest_by_id,
    get_all_guests,
    delete_guest_application,
)
from app.utils.dependencies import DbSession

router = APIRouter(prefix="/guest-application", tags=["Guest Application"])


@router.post("/", response_model=GuestOut, status_code=status.HTTP_201_CREATED)
def submit_guest_application(payload: GuestCreate, request: Request, db: DbSession):
    ip_address = request.client.host
    return create_guest_application(db, payload, ip_address)


@router.get("/", response_model=list[GuestOut])
def list_guest_applications(db: DbSession):
    return get_all_guests(db)


@router.get("/{guest_id}", response_model=GuestOut)
def get_guest_application(guest_id: UUID, db: DbSession):
    return get_guest_by_id(db, guest_id)


@router.delete("/{guest_id}")
def remove_guest_application(guest_id: UUID, db: DbSession):
    return delete_guest_application(db, guest_id)
