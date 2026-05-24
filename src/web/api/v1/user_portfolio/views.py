from uuid import UUID

from fastapi import APIRouter, Security, status

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.portfolio_item.schema import (
    CreatePortfolioItemSchema,
    PortfolioItemDTO,
    ReplaceUserSkillsSchema,
    UpdatePortfolioItemSchema,
)
from src.service.skill.schema import SkillDTO
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    PortfolioItemServiceDep,
    get_current_verified_user,
)

router = APIRouter(prefix=settings.api.v1.users)


@router.get("/portfolio-items")
async def get_my_portfolio_items(
    service: PortfolioItemServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.PORTFOLIO_ITEMS_LIST],
    ),
) -> list[PortfolioItemDTO]:
    return await service.get_current_user_items(current_user.id)


@router.post("/portfolio-items", status_code=status.HTTP_201_CREATED)
async def create_my_portfolio_item(
    data: CreatePortfolioItemSchema,
    service: PortfolioItemServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.PORTFOLIO_ITEMS_CREATE],
    ),
) -> PortfolioItemDTO:
    return await service.create(current_user.id, data)


@router.get("/portfolio-items/{item_id}")
async def get_my_portfolio_item(
    item_id: UUID,
    service: PortfolioItemServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.PORTFOLIO_ITEMS_DETAIL],
    ),
) -> PortfolioItemDTO:
    return await service.get_current_user_item(current_user.id, item_id)


@router.patch("/portfolio-items/{item_id}")
async def update_my_portfolio_item(
    item_id: UUID,
    data: UpdatePortfolioItemSchema,
    service: PortfolioItemServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.PORTFOLIO_ITEMS_UPDATE],
    ),
) -> PortfolioItemDTO:
    return await service.update(current_user.id, item_id, data)


@router.delete(
    "/portfolio-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_my_portfolio_item(
    item_id: UUID,
    service: PortfolioItemServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.PORTFOLIO_ITEMS_DELETE],
    ),
) -> None:
    await service.delete(current_user.id, item_id)


@router.get("/{user_id}/portfolio-items")
async def get_user_portfolio_items(
    user_id: UUID,
    service: PortfolioItemServiceDep,
    _: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.PORTFOLIO_ITEMS_LIST],
    ),
) -> list[PortfolioItemDTO]:
    return await service.get_by_user_id(user_id)


@router.get("/skills")
async def get_my_skills(
    service: PortfolioItemServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.USER_SKILLS_LIST],
    ),
) -> list[SkillDTO]:
    return await service.get_current_user_skills(current_user.id)


@router.put("/skills")
async def replace_my_skills(
    data: ReplaceUserSkillsSchema,
    service: PortfolioItemServiceDep,
    current_user: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.USER_SKILLS_UPDATE],
    ),
) -> list[SkillDTO]:
    return await service.replace_current_user_skills(current_user.id, data)


@router.get("/{user_id}/skills")
async def get_user_skills(
    user_id: UUID,
    service: PortfolioItemServiceDep,
    _: UserDTO = Security(
        get_current_verified_user,
        scopes=[Scope.USER_SKILLS_LIST],
    ),
) -> list[SkillDTO]:
    return await service.get_user_skills(user_id)
