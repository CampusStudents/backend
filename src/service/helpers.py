from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints, BaseModel

NonEmptyStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]

class ShortDTO(BaseModel):
    id: UUID
    name: str