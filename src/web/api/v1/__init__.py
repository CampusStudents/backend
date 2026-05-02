from fastapi import APIRouter

from src.core.config import settings

from .auth import router as auth_router
from .cities import router as cities_router
from .projects import router as projects_router
from .skills import router as skills_router
from .team_roles import router as team_roles_router
from .universities import router as universities_router
from .user_profiles import router as user_profiles_router
from .users import router as users_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(auth_router, prefix=settings.api.v1.auth)
router.include_router(cities_router, tags=["Cities"])
router.include_router(projects_router, tags=["Projects"])
router.include_router(skills_router, tags=["Skills"])
router.include_router(team_roles_router, tags=["Team roles"])
router.include_router(universities_router, tags=["Universities"])
router.include_router(user_profiles_router, tags=["User profiles"])
router.include_router(users_router, tags=["Users"])
