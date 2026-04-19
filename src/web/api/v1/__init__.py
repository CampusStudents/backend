from fastapi import APIRouter

from src.core.config import settings

from .auth import router as auth_router
from .cities import router as cities_router
from .universities import router as universities_router
from .users import router as users_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(auth_router, prefix=settings.api.v1.auth)
router.include_router(cities_router, tags=["Cities"])
router.include_router(universities_router, tags=["Universities"])
router.include_router(users_router, tags=["Users"])
