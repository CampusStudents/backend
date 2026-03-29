from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    type: str = "Bearer"


class TokenPair(AccessToken):
    refresh_token: str
