from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork
from .schema import RegisterSchema, UserDTO
from src.core.exceptions.service.base import AlreadyExistsError
from src.core.security.utils import get_password_hash


class UserService:
    def __init__(self, uow: UnitOfWork, repository: UserRepository):
        self.uow = uow
        self.repository = repository

    async def get_by_email(self, email: str):
        async with self.uow as uow:
            user = await self.repository.get_by_filters(uow.session, {"email": email})
            if user:
                return UserDTO.model_validate(user)
            return None

    async def register(self, data: RegisterSchema):
        async with self.uow as uow:
            existing_user = await self.repository.get_by_filters(
                uow.session, {"email": data.email}
            )
            if existing_user:
                raise AlreadyExistsError("Email already exists")
            user = await self.repository.create(
                uow.session,
                {
                    "email": data.email,
                    "password_hash": get_password_hash(
                        data.password.get_secret_value()
                    ),
                    "role": data.role.value,
                },
            )
            await uow.commit()
            return UserDTO.model_validate(user)
