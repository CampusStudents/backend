from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions.service.auth import (
    InvalidTokenError,
    NotAuthenticatedError,
)
from src.core.exceptions.service.base import AuthError
from src.core.exceptions.service.user import UserNotFoundError
from src.core.security.rbac import get_user_scopes
from src.core.security.send_email import (
    verify_password_reset_token,
    verify_verification_token,
)
from src.core.security.token import TokenPair
from src.core.security.utils import (
    decode_jwt,
    encode_jwt,
    get_password_hash,
    verify_password,
)
from src.db.models import User
from src.db.repository.refresh_session import RefreshSessionRepository
from src.db.repository.user import UserRepository
from src.db.unit_of_work import UnitOfWork
from src.service.user.schema import UserDTO

from .schema import LoginSchema


class AuthService:
    def __init__(
        self,
        uow: UnitOfWork,
        session_repository: RefreshSessionRepository,
        user_repository: UserRepository,
    ):
        self.uow = uow
        self.session_repository = session_repository
        self.user_repository = user_repository

    async def _get_user_by_email(
        self, session: AsyncSession, email: str
    ) -> User | None:
        return await self.user_repository.get_out(session, {"email": email})

    async def _get_user_by_email_with_roles(
        self, session: AsyncSession, email: str
    ) -> User | None:
        return await self.user_repository.get_out(session, {"email": email})

    async def _get_user_by_email_or_raise(
        self, session: AsyncSession, email: str
    ) -> User:
        user = await self._get_user_by_email(session, email)
        if not user:
            msg = f"User with email {email} not exists"
            raise UserNotFoundError(msg)
        return user

    @classmethod
    def _create_token(
        cls, payload: dict, token_type: str, expires_in: timedelta
    ) -> str:
        jwt_payload = {"type": token_type}
        jwt_payload.update(payload)
        return encode_jwt(jwt_payload, expires_in)

    def _create_access_token(self, user: User):
        payload = {
            "sub": user.email,
            "user_id": str(user.id),
            settings.auth.token_version_field: user.token_version,
        }
        return self._create_token(
            payload=payload,
            token_type=settings.auth.access_token_type,
            expires_in=timedelta(minutes=settings.auth.access_token_expire_minutes),
        )

    async def _create_refresh_token(self, session: AsyncSession, user: User):
        payload = {
            "sub": user.email,
            "jti": str(uuid4()),
        }
        token = self._create_token(
            payload=payload,
            token_type=settings.auth.refresh_token_type,
            expires_in=timedelta(days=settings.auth.refresh_token_expire_days),
        )
        await self.session_repository.create(
            session,
            {
                "refresh_jti": payload["jti"],
                "expires_at": datetime.now()
                + timedelta(days=settings.auth.refresh_token_expire_days),
                "user_id": user.id,
            },
        )
        return token

    async def _create_auth_tokens(self, session: AsyncSession, user: User) -> TokenPair:
        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(session, user)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def login(self, data: LoginSchema) -> TokenPair:
        async with self.uow as uow:
            user = await self._get_user_by_email(uow.session, data.email)
            if not user or not verify_password(
                data.password.get_secret_value(), user.password_hash
            ):
                raise NotAuthenticatedError
            tokens = await self._create_auth_tokens(uow.session, user)
            await uow.commit()
            return tokens

    async def refresh_token(self, token: str) -> TokenPair:
        async with self.uow as uow:
            payload = decode_jwt(token)
            if payload.get("type") != settings.auth.refresh_token_type:
                raise InvalidTokenError
            jti = payload.get("jti")
            if not jti:
                raise InvalidTokenError

            token_obj = await self.session_repository.get_out(
                uow.session, {"refresh_jti": jti}
            )
            if not token_obj:
                raise InvalidTokenError

            email = payload.get("sub")
            user = await self._get_user_by_email(uow.session, email)
            if not user:
                raise InvalidTokenError

            new_tokens = await self._create_auth_tokens(uow.session, user)
            await self.session_repository.delete_by_jti(uow.session, jti)
            await uow.commit()

            return new_tokens

    async def get_current_user(self, payload: dict) -> UserDTO:
        if payload.get("type") != settings.auth.access_token_type:
            raise NotAuthenticatedError

        email = payload.get("sub")
        token_version = payload.get(settings.auth.token_version_field)
        if not email or token_version is None:
            raise NotAuthenticatedError

        async with self.uow as uow:
            user = await self._get_user_by_email_with_roles(uow.session, email)
            if not user or user.token_version != token_version:
                raise NotAuthenticatedError
            scopes = get_user_scopes(user)
            dto = UserDTO.model_validate(user)
            dto.scopes = scopes
            return dto

    async def logout(self, refresh_token: str) -> None:
        async with self.uow as uow:
            try:
                payload = decode_jwt(refresh_token)
            except InvalidTokenError:
                return
            jti = payload.get("jti")
            if jti:
                await self.session_repository.delete_by_jti(uow.session, jti)
            await uow.commit()

    async def change_password(
        self, email: str, old_password: str, new_password: str
    ) -> None:
        async with self.uow as uow:
            user = await self._get_user_by_email_or_raise(uow.session, email)
            if not verify_password(old_password, user.password_hash):
                msg = "Invalid old password"
                raise AuthError(msg)
            user.password_hash = get_password_hash(new_password)
            # Можно также удалить все сессии пользователя
            await uow.commit()

    async def logout_all(self, user_id: UUID):
        async with self.uow as uow:
            await self.session_repository.delete_by_user_id(uow.session, user_id)
            user = await self.user_repository.get(uow.session, {"id": user_id})
            if user:
                user.token_version += 1
            await uow.commit()

    async def verify_account(self, token: str):
        async with self.uow as uow:
            payload = verify_verification_token(token)
            if payload is None:
                raise InvalidTokenError

            email = payload.get("sub")
            user = await self._get_user_by_email(uow.session, email)
            if user is None:
                raise InvalidTokenError

            if user.is_verified:
                return

            user.is_verified = True
            await uow.commit()

    async def reset_password(self, token: str, new_password: str):
        """Сброс пароля по токену восстановления"""
        async with self.uow as uow:
            session = uow.session
            payload = verify_password_reset_token(token)
            if payload is None:
                raise InvalidTokenError

            email = payload.get("sub")
            user = await self._get_user_by_email(session, email)
            if user is None:
                raise InvalidTokenError

            user.password_hash = get_password_hash(new_password)
            # Завершаем все активные сессии пользователя для безопасности
            await self.session_repository.delete_by_user_id(
                session=session, user_id=user.id
            )
            user.token_version += 1

            await uow.commit()
