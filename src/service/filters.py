from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class BaseFilter(BaseModel):
    limit: Annotated[int | None, Field(ge=1)] = None
    offset: Annotated[int, Field(ge=0)] = 0

    model_config = ConfigDict(populate_by_name=True)

    def to_repository_filters(self) -> dict:
        return self.model_dump(exclude_none=True)
