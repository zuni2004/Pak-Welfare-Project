from fastapi import APIRouter, FastAPI

from app.features.auth.router import router as auth_router
from app.features.service_types.router import router as service_types_router
from app.admin.auth.router import router as admin_auth_router
from app.features.guest_applications.router import router as guest_routers
from app.features.noc_application.router import router as NOC_routers

api_router = APIRouter(prefix="/api")

api_router.include_router(admin_auth_router)
api_router.include_router(auth_router)
api_router.include_router(service_types_router) 
api_router.include_router(guest_routers)
api_router.include_router(NOC_routers)


def register_routes(app: FastAPI):
    app.include_router(api_router)
