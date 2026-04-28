import logging
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from jwt import ExpiredSignatureError, PyJWTError

from src.core.config import settings
from src.core.exceptions.service.auth import InvalidTokenError, TokenExpiredError

logger = logging.getLogger(__name__)


def encode_jwt(
        payload: dict,
        expires_in: timedelta,
        private_key: str = settings.auth.private_key_path.read_text(),
        algorithm: str = settings.auth.algorithm,
):
    to_encode = payload.copy()
    now = datetime.now(UTC)
    expire = now + expires_in
    to_encode.update(iat=now, exp=expire)
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded_jwt


def decode_jwt(
        jwt_token: str | bytes,
        public_key: str = settings.auth.public_key_path.read_text(),
        algorithm: str = settings.auth.algorithm,
) -> dict:
    try:
        decoded_jwt = jwt.decode(jwt_token, public_key, algorithms=[algorithm])
    except ExpiredSignatureError as err:
        msg = "JWT expired"
        logger.info(msg)
        raise TokenExpiredError(msg) from err
    except PyJWTError as err:
        logger.error("Error decoding jwt token", exc_info=True)
        msg = "Error decoding jwt token"
        raise InvalidTokenError(msg) from err
    return decoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
