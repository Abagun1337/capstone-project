from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class User(UserRead):
    pass
