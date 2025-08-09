import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from .schema import (
    ServiceTypeCreate,
    ServiceTypeUpdate,
    ServiceTypeOut,
)
from .service import (
    create_service_type,
    get_service_types,
    get_service_type_by_id,
    update_service_type
)
from app.utils.dependencies import DbSession

router = APIRouter(prefix="/serviceType", tags=["ServiceType"])

@router.post("/", response_model=ServiceTypeOut, status_code=status.HTTP_201_CREATED)
async def create_service(request: Request, payload: ServiceTypeCreate, db: DbSession):
    return create_service_type(db, payload)

@router.get("/", response_model=list[ServiceTypeOut], status_code=status.HTTP_200_OK)
async def list_services(request: Request, db: DbSession):
    return get_service_types(db)

@router.get("/{id}", response_model=ServiceTypeOut, status_code=status.HTTP_200_OK)
async def get_service(id: uuid.UUID, db: DbSession):
    service = get_service_type_by_id(db, id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.put("/{id}", response_model=ServiceTypeOut)
async def update_service(id: uuid.UUID, payload: ServiceTypeUpdate, db: DbSession):
    return update_service_type(db, id, payload)
