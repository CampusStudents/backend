import logging
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, Response, Security
from pydantic import BaseModel, EmailStr

from src.core.config import settings
from src.core.exceptions.service.auth import InvalidTokenError, TokenExpiredError
from src.core.exceptions.service.base import BadRequestError
from src.core.security.scopes import Scope
from src.core.security.send_email import (
    send_password_reset_email,
    send_verification_email,
)
from src.core.security.token import AccessToken
from src.service.auth.schema import (
    ChangePasswordSchema,
    LoginSchema,
    ResetPasswordSchema,
)
from src.service.user.schema import RegisterSchema, UserDTO
from src.web.api.dependencies import (
    AuthServiceDep,
    UserServiceDep,
    get_current_active_user,
    get_current_verified_user,
    get_token_for_refresh,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/me")
async def get_user(
        user: UserDTO = Security(
            get_current_verified_user, scopes=[Scope.AUTH_ME]
        ),
):
    """
    Получение текущего пользователя.
    """
    return user


def set_refresh_token_to_response(response: Response, token: str):
    max_age = int(
        timedelta(days=settings.auth.refresh_token_expire_days).total_seconds()
    )
    response.set_cookie(
        "refresh_token",
        token,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        # secure=True,
    )


@router.post("/login")
async def login(
        data: LoginSchema, auth_service: AuthServiceDep, response: Response
) -> AccessToken:
    """
    Аутентификация пользователя.
    Возвращает access token, refresh token устанавливается в HTTP-only cookie.
    """
    tokens = await auth_service.login(data)
    set_refresh_token_to_response(response, tokens.refresh_token)
    return AccessToken(access_token=tokens.access_token)


@router.post("/register")
async def register(
        data: RegisterSchema,
        user_service: UserServiceDep,
        background_tasks: BackgroundTasks,
) -> UserDTO:
    """
    Регистрация нового пользователя.
    Отправляет email с подтверждением.
    """
    user = await user_service.register(data)
    background_tasks.add_task(send_verification_email, str(user.email))
    return user


@router.post("/refresh")
async def refresh_jwt(
        response: Response,
        auth_service: AuthServiceDep,
        token: str = Depends(get_token_for_refresh),
) -> AccessToken:
    """
    Обновление пары токенов с использованием refresh token из cookie.
    """
    new_tokens = await auth_service.refresh_token(token)
    set_refresh_token_to_response(response, new_tokens.refresh_token)
    return AccessToken(access_token=new_tokens.access_token)


@router.post("/logout")
async def logout(
        response: Response,
        auth_service: AuthServiceDep,
        _user: UserDTO = Security(get_current_verified_user, scopes=[Scope.AUTH_LOGOUT]),
        token: str = Depends(get_token_for_refresh),
) -> None:
    """
    Выход из системы.
    Инвалидирует refresh token и удаляет cookie.
    """
    await auth_service.logout(token)
    response.delete_cookie("refresh_token")


@router.post("/change_password")
async def change_password(
        data: ChangePasswordSchema,
        auth_service: AuthServiceDep,
        user: UserDTO = Security(
            get_current_verified_user, scopes=[Scope.AUTH_CHANGE_PASSWORD]
        ),
) -> None:
    """
    Смена пароля текущего пользователя.
    """
    await auth_service.change_password(
        email=user.email,
        old_password=data.old_password.get_secret_value(),
        new_password=data.new_password.get_secret_value(),
    )


@router.post("/quit_all")
async def quit_all(
        response: Response,
        auth_service: AuthServiceDep,
        user: UserDTO = Security(
            get_current_verified_user, scopes=[Scope.AUTH_QUIT_ALL]
        ),
) -> None:
    """
    Завершение всех сессий пользователя.
    """
    await auth_service.logout_all(user.id)
    response.delete_cookie("refresh_token")


@router.get("/verify")
async def verify_account(
        token: str,
        service: AuthServiceDep,
):
    """
    Подтверждение email (JSON).
    Ссылка из письма ведет сюда.
    """
    try:
        await service.verify_account(token)
    except (InvalidTokenError, TokenExpiredError):
        raise BadRequestError(detail="Invalid or expired token") # noqa: B904
    else:
        return {"message": "Account successfully verified"}


@router.post("/resend_verification")
async def resend_verification(
        background_tasks: BackgroundTasks,
        user: UserDTO = Security(
            get_current_active_user, scopes=[Scope.AUTH_RESEND_VERIFICATION]
        ),
):
    """
    Повторная отправка письма с подтверждением email.
    """
    if user.is_verified:
        raise BadRequestError(detail="Email already verified")

    background_tasks.add_task(send_verification_email, str(user.email))
    return {"message": "Письмо с верификацией отправлено"}


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


@router.post("/forgot_password")
async def forgot_password(
        data: ForgotPasswordSchema,
        background_tasks: BackgroundTasks,
        user_service: UserServiceDep,
):
    """
    Запрос на восстановление пароля.
    Отправляет письмо с токеном для сброса пароля.
    Всегда возвращает успех, чтобы не раскрывать существование email в системе.
    """
    # Проверяем существование пользователя
    try:
        user = await user_service.get_by_email(data.email)
        if user:
            background_tasks.add_task(send_password_reset_email, str(data.email))
    except Exception as e:
        # Игнорируем любые ошибки, чтобы не раскрывать информацию о существовании email
        logger.warning(
            f"Error during password reset request for {data.email}: {e}"
        )
    return {
        "message": (
            "Если указанный email зарегистрирован, на него "
            "будет отправлено письмо с инструкцией по восстановлению пароля"
        )
    }


@router.post("/reset_password")
async def reset_password(
        data: ResetPasswordSchema,
        service: AuthServiceDep,
):
    """
    Сброс пароля по токену из письма.
    """
    try:
        await service.reset_password(data.token, data.new_password.get_secret_value())
    except (InvalidTokenError, TokenExpiredError):
        raise BadRequestError(detail="Invalid or expired token") from None
    return {"message": "Пароль успешно изменен"}

