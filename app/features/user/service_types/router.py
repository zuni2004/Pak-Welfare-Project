from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from .schema import (
    ServiceTypeResponse,
)
from .service import (
    get_service_types,
    get_service_type_by_id,
)
from app.utils.dependencies import DbSession

router = APIRouter(prefix="/service-type", tags=["Service Type"])


@router.get(
    "/", response_model=List[ServiceTypeResponse], status_code=status.HTTP_200_OK
)
async def list_services(db: DbSession):
    return get_service_types(db=db)


@router.get("/{id}", response_model=ServiceTypeResponse, status_code=status.HTTP_200_OK)
async def get_service(id: UUID, db: DbSession):
    return get_service_type_by_id(id=id, db=db)
