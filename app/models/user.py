from typing import Union
from pydantic import BaseModel


class User(BaseModel):
    id: Union[str, None] = None
    email: Union[str, None] = None
    password: Union[str, None] = None
    password_digest: Union[str, None] = None


class NewUser(BaseModel):
    email: Union[str, None] = None
    password: Union[str, None] = None


class UserPublic(BaseModel):
    id: Union[str, None] = None
    email: Union[str, None] = None
