from uuid import UUID

from src.db.models import ProjectVacancy
from src.db.repository.project_vacancy import ProjectVacancyRepository
from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork
from src.service.helpers import ShortDTO
from src.service.user.schema import UserDTO

from .schema import VacancyRecommendationDTO, VacancyRecommendationFilter


class RecommendationService:
    def __init__(
        self,
        uow: UnitOfWork,
        vacancy_repository: ProjectVacancyRepository,
        user_repository: UserRepository,
    ):
        self.uow = uow
        self.vacancy_repository = vacancy_repository
        self.user_repository = user_repository

    async def get_vacancy_recommendations(
        self,
        user: UserDTO,
        filters: VacancyRecommendationFilter,
    ) -> list[VacancyRecommendationDTO]:
        async with self.uow as uow:
            user_with_skills = await self.user_repository.get_with_skills(
                uow.session,
                user.id,
            )
            user_skill_ids = (
                {skill.id for skill in user_with_skills.skills}
                if user_with_skills
                else set()
            )
            vacancies = await self.vacancy_repository.get_recommended_for_user(
                uow.session,
                user.id,
                {
                    "skill_id": filters.skill_id,
                    "team_role_id": filters.team_role_id,
                    "event_id": filters.event_id,
                    "city_id": filters.city_id,
                    "status": filters.status,
                    "format": filters.format,
                    "type": filters.type,
                },
            )
            recommendations = [
                self._build_recommendation(vacancy, user_skill_ids)
                for vacancy in vacancies
            ]
            sorted_recommendations = sorted(
                recommendations,
                key=lambda item: (
                    -item.matching_skill_count,
                    item.missing_skill_count,
                    item.created_at,
                    item.id,
                ),
            )
            if filters.limit is None:
                return sorted_recommendations[filters.offset :]
            return sorted_recommendations[
                filters.offset : filters.offset + filters.limit
            ]

    def _build_recommendation(
        self,
        vacancy: ProjectVacancy,
        user_skill_ids: set[UUID],
    ) -> VacancyRecommendationDTO:
        matched_skills = [
            ShortDTO.model_validate(skill)
            for skill in vacancy.skills
            if skill.id in user_skill_ids
        ]
        missing_skills = [
            ShortDTO.model_validate(skill)
            for skill in vacancy.skills
            if skill.id not in user_skill_ids
        ]
        return VacancyRecommendationDTO.model_validate(
            {
                "id": vacancy.id,
                "created_at": vacancy.created_at,
                "updated_at": vacancy.updated_at,
                "project_id": vacancy.project_id,
                "team_role_id": vacancy.team_role_id,
                "required_count": vacancy.required_count,
                "description": vacancy.description,
                "team_role": vacancy.team_role,
                "project": vacancy.project,
                "skills": vacancy.skills,
                "matching_skill_count": len(matched_skills),
                "missing_skill_count": len(missing_skills),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
            },
        )
