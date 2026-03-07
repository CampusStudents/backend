from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    foo: int
    bar: int


class UserCreate(BaseModel):
    pass


class UserRead(BaseModel):
    id: str
