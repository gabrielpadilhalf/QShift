from fastapi import APIRouter

from core_api.core.config import settings
from core_api.api.routes.availabilities import router as availabilities_router
from core_api.api.routes.employees import router as employees_router
from core_api.api.routes.shifts import router as shifts_router
from core_api.api.routes.weeks import router as weeks_router
from core_api.api.routes.dev import router as dev_router
from core_api.api.routes.schedule import router as schedule_router
from core_api.api.routes.users import router as users_router
from core_api.api.routes.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(availabilities_router)
api_router.include_router(employees_router)
api_router.include_router(shifts_router)
api_router.include_router(weeks_router)
api_router.include_router(schedule_router)
api_router.include_router(users_router)
api_router.include_router(auth_router)

if settings.ENV in {"dev", "test"}:
    api_router.include_router(dev_router)
