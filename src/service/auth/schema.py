from pydantic import BaseModel, EmailStr, SecretStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: SecretStr


class ChangePasswordSchema(BaseModel):
    old_password: SecretStr
    new_password: SecretStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: SecretStr
