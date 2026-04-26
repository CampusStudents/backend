from uuid import UUID

from src.core.exceptions.service.base import AlreadyExistsError, BadRequestError
from src.core.exceptions.service.user import UserNotFoundError
from src.core.security.utils import get_password_hash
from src.db.repository.role import RoleRepository
from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork

from .schema import RegisterSchema, UpdateUserRolesSchema, UserDTO


class UserService:
    def __init__(
            self,
            uow: UnitOfWork,
            repository: UserRepository,
            role_repository: RoleRepository,
    ):
        self.uow = uow
        self.repository = repository
        self.role_repository = role_repository

    async def get_by_email(self, email: str):
        async with self.uow as uow:
            user = await self.repository.get_out(uow.session, {"email": email})
            if user:
                return UserDTO.model_validate(user)
            return None

    async def register(self, data: RegisterSchema):
        async with self.uow as uow:
            existing_user = await self.repository.get_out(
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
                },
            )

            roles = await self.role_repository.get_multi(
                uow.session,
                {"name": ["public", "user"]},
            )
            if len(roles) != 2:
                raise BadRequestError("User roles is not configured")

            await self.repository.assign_roles(
                uow.session, user_id=user.id, role_ids=[role.id for role in roles]
            )
            await uow.commit()
            user_with_roles = await self.repository.get_out(
                uow.session,
                {"id": user.id},
            )
            return UserDTO.model_validate(user_with_roles or user)

    async def update_roles(self, user_id: UUID, data: UpdateUserRolesSchema) -> UserDTO:
        async with self.uow as uow:
            user = await self.repository.get_out(uow.session, {"id": user_id})
            if not user:
                raise UserNotFoundError("User not found")

            roles = await self.role_repository.get_multi(
                uow.session,
                {"name": data.roles},
            )
            if len(roles) != len(data.roles):
                raise BadRequestError("One or more roles not found")

            await self.repository.replace_roles(
                uow.session, user_id=user.id, role_ids=[role.id for role in roles]
            )
            await uow.session.refresh(user, attribute_names=["roles"])
            await uow.commit()
            return UserDTO.model_validate(user)
