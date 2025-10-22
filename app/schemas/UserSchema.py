import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.db.User import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = "None"
    surname: str | None = "None"
    role: UserRole = UserRole.USER


class UserReadSchema(UserBase):
    is_verified: bool
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserSignIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
