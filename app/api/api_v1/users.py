from core.config import settings
from core.models import db_helper
from core.schemas.user import UserRead
from crud.users import get_all_users
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix=settings.api.v1.users, tags=["Users"])


@router.get("", response_model=list[UserRead])
async def get_users(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    await get_all_users(session=session)
