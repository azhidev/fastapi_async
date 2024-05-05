from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str

    class from_attributes:
        orm_mode = True


class LoginUser(BaseModel):
    username: str
    password: str


class RegisterModel(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str
    password: str = None


class Token(BaseModel):
    access_token: str
    token_type: str


class Permission(BaseModel):
    name: str
    codename: str

    class from_attributes:
        orm_mode = True


class PermissionCreate(BaseModel):
    name: str
    codename: str


class PermissionUpdate(BaseModel):
    name: str = None
    codename: str = None