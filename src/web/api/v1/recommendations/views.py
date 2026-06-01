from typing import Annotated

from fastapi import APIRouter, Query, Security

from src.core.config import settings
from src.core.security.scopes import Scope
from src.service.recommendation.schema import (
    VacancyRecommendationDTO,
    VacancyRecommendationFilter,
)
from src.service.user.schema import UserDTO
from src.web.api.dependencies import (
    RecommendationServiceDep,
    get_current_active_user_with_profile,
)

router = APIRouter(prefix=settings.api.v1.recommendations)


@router.get("/vacancies")
async def get_vacancy_recommendations(
    service: RecommendationServiceDep,
    filters: Annotated[VacancyRecommendationFilter, Query()],
    user: UserDTO = Security(
        get_current_active_user_with_profile,
        scopes=[Scope.RECOMMENDATIONS_VACANCIES],
    ),
) -> list[VacancyRecommendationDTO]:
    return await service.get_vacancy_recommendations(user, filters)
