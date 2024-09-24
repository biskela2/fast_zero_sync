from turtle import config_dict

from pydantic import BaseModel, EmailStr, ConfigDict


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = config_dict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]
