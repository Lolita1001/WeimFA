from typing import Optional

from sqlmodel import Field

from models.user.base import UserBase, MediaUserBase


class UserCreate(UserBase):
    password: str = Field(schema_extra={'c_required': True})


class UserUpdate(UserCreate):
    old_password: str = Field(schema_extra={'c_required': True})


class UserUpdateAdmin(UserBase):
    is_admin: bool = Field(schema_extra={'c_required': True})
    is_active: bool = Field(schema_extra={'c_required': True})


class MediaUserCreate(MediaUserBase):
    user_id: Optional[int] = Field(foreign_key='user.id')