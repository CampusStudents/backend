import logging
from email.message import EmailMessage

import aiosmtplib

from .utils import encode_jwt, decode_jwt
from src.core.exceptions.service.auth import InvalidTokenError, TokenExpiredError
from src.core.config import settings

logger = logging.getLogger(__name__)

TOKEN_PURPOSE_FIELD = "purpose"
VERIFY_EMAIL_PURPOSE = "verify_email"
PASSWORD_RESET_PURPOSE = "password_reset"

VERIFY_EMAIL_EXPIRE_MINUTES = 3
PASSWORD_RESET_EXPIRE_MINUTES = 15


async def send_email(
        from_email: str,
        to_email: str,
        subject: str,
        body: str,
):
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    await aiosmtplib.send(
        message, hostname=settings.email.smtp_host, port=settings.email.smtp_port
    )


def generate_link_for_verification(token: str) -> str:
    return f"{settings.app_url}/api/v1/auth/verify?token={token}"


def _create_service_token(email: str, expire_minutes: int, purpose: str) -> str:
    payload = {"sub": email, TOKEN_PURPOSE_FIELD: purpose}
    return encode_jwt(payload, expire_minutes)


def _verify_service_token(token: str, expected_purpose: str):
    try:
        payload = decode_jwt(token)
    except TokenExpiredError:
        raise
    except InvalidTokenError:
        return None

    if payload.get(TOKEN_PURPOSE_FIELD) != expected_purpose:
        return None
    return payload


def create_token_for_verification(email: str):
    return _create_service_token(
        email, VERIFY_EMAIL_EXPIRE_MINUTES, VERIFY_EMAIL_PURPOSE
    )


async def send_verification_email(
        email: str,
):
    token = create_token_for_verification(email)
    await send_email(
        from_email=settings.email.from_email,
        to_email=email,
        subject="Подтверждение регистрации на Campus",
        body=f"Для подтверждения регистрации перейдите по ссылке {generate_link_for_verification(token)}",
    )


def verify_verification_token(token: str):
    return _verify_service_token(token, VERIFY_EMAIL_PURPOSE)


def create_token_for_password_reset(email: str):
    return _create_service_token(
        email, PASSWORD_RESET_EXPIRE_MINUTES, PASSWORD_RESET_PURPOSE
    )


def generate_link_for_password_reset(token: str) -> str:
    return f"{settings.app_url}/reset-password?token={token}"


async def send_password_reset_email(email: str):
    token = create_token_for_password_reset(email)
    await send_email(
        from_email=settings.email.from_email,
        to_email=email,
        subject="Восстановление пароля на Campus",
        body=f"Для сброса пароля перейдите по ссылке: {generate_link_for_password_reset(token)}. Ссылка действительна {PASSWORD_RESET_EXPIRE_MINUTES} минут.",
    )


def verify_password_reset_token(token: str):
    return _verify_service_token(token, PASSWORD_RESET_PURPOSE)
