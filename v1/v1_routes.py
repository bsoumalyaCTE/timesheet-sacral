from fastapi import APIRouter
from .routes.user_routes import user_router
from .routes.customer_routes import customer_router
from .routes.project_routes import project_router

version_v1 = APIRouter(prefix="/v1", tags=["API 1.0"])

# Include user and project routes
version_v1.include_router(user_router)
version_v1.include_router(customer_router)
version_v1.include_router(project_router)