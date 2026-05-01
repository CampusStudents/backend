import logging
from datetime import timedelta
from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core.config import settings
from src.core.exceptions.service.auth import InvalidTokenError, TokenExpiredError

from .utils import decode_jwt, encode_jwt

logger = logging.getLogger(__name__)

TOKEN_PURPOSE_FIELD = "purpose"
VERIFY_EMAIL_PURPOSE = "verify_email"
PASSWORD_RESET_PURPOSE = "password_reset"

VERIFY_EMAIL_EXPIRE_MINUTES = 3
PASSWORD_RESET_EXPIRE_MINUTES = 15

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates" / "emails"
email_templates = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(enabled_extensions=("html", "j2")),
)


async def send_email(
        from_email: str,
        to_email: str,
        subject: str,
        body: str,
        html_body: str | None = None,
):
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    if html_body:
        message.add_alternative(html_body, subtype="html")
    await aiosmtplib.send(
        message, hostname=settings.email.smtp_host, port=settings.email.smtp_port
    )


def render_email_template(template_name: str, **context) -> str:
    template = email_templates.get_template(template_name)
    return template.render(
        app_name="Campus",
        from_email=settings.email.from_email,
        **context,
    )


def get_app_url() -> str:
    app_url = settings.app_url.rstrip("/")
    if app_url.startswith(("http://", "https://")):
        return app_url
    return f"http://{app_url}"


def generate_link_for_verification(token: str) -> str:
    return f"{get_app_url()}/api/v1/auth/verify?token={token}"


def _create_service_token(email: str, expires_in: timedelta, purpose: str) -> str:
    payload = {"sub": email, TOKEN_PURPOSE_FIELD: purpose}
    return encode_jwt(payload, expires_in)


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
        email, timedelta(minutes=VERIFY_EMAIL_EXPIRE_MINUTES), VERIFY_EMAIL_PURPOSE
    )


async def send_verification_email(
        email: str,
):
    token = create_token_for_verification(email)
    verification_link = generate_link_for_verification(token)
    await send_email(
        from_email=settings.email.from_email,
        to_email=email,
        subject="Подтверждение регистрации на Campus",
        body=(
            "Для подтверждения регистрации перейдите по ссылке: "
            f"{verification_link}. Ссылка действительна "
            f"{VERIFY_EMAIL_EXPIRE_MINUTES} минут."
        ),
        html_body=render_email_template(
            "verify_email.html.j2",
            email=email,
            verification_link=verification_link,
            expires_minutes=VERIFY_EMAIL_EXPIRE_MINUTES,
        ),
    )


def verify_verification_token(token: str):
    return _verify_service_token(token, VERIFY_EMAIL_PURPOSE)


def create_token_for_password_reset(email: str):
    return _create_service_token(
        email, timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES), PASSWORD_RESET_PURPOSE
    )


def generate_link_for_password_reset(token: str) -> str:
    return f"{get_app_url()}/reset-password?token={token}"


async def send_password_reset_email(email: str):
    token = create_token_for_password_reset(email)
    reset_link = generate_link_for_password_reset(token)
    await send_email(
        from_email=settings.email.from_email,
        to_email=email,
        subject="Восстановление пароля на Campus",
        body=(
            "Для сброса пароля перейдите по ссылке: "
            f"{reset_link}. Ссылка действительна "
            f"{PASSWORD_RESET_EXPIRE_MINUTES} минут."
        ),
        html_body=render_email_template(
            "password_reset.html.j2",
            email=email,
            reset_link=reset_link,
            expires_minutes=PASSWORD_RESET_EXPIRE_MINUTES,
        ),
    )


def verify_password_reset_token(token: str):
    return _verify_service_token(token, PASSWORD_RESET_PURPOSE)
