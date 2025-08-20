from fastapi import APIRouter, FastAPI

from app.features.user.auth.router import router as auth_router
from app.features.user.service_types.router import router as service_types_router
from app.features.admin.auth.router import router as admin_auth_router
from app.features.user.guest.router import router as guest_router
from app.features.user.noc_application.router import router as NOC_router
from app.features.user.document.router import router as document_router

api_router = APIRouter(prefix="/api")

api_router.include_router(admin_auth_router)
api_router.include_router(auth_router)
api_router.include_router(service_types_router)
api_router.include_router(guest_router)
api_router.include_router(NOC_router)
api_router.include_router(document_router)


def register_routes(app: FastAPI):
    app.include_router(api_router)
