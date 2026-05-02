from pydantic import BaseModel

from src.service.filters import BaseFilter
from src.service.helpers import EntityDTO, NonEmptyStr


class SkillBaseSchema(BaseModel):
    name: NonEmptyStr


class CreateSkillSchema(SkillBaseSchema):
    pass


class UpdateSkillSchema(BaseModel):
    name: NonEmptyStr | None = None


class SkillFilter(BaseFilter):
    name: NonEmptyStr | None = None
    name__like: str | None = None


class SkillDTO(SkillBaseSchema, EntityDTO):
    pass
