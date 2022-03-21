from typing import Optional, List
import enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, VARCHAR
from pydantic import EmailStr
from uuid import UUID, uuid4  # TODO уточнить в каких случаях используют uuid
from datetime import datetime


class Privileges(str, enum.Enum):
    user = 'User'
    admin = 'Admin'
    visitor = 'Visitor'


class BaseUser(SQLModel):
    login: str = Field(sa_column=Column("login", VARCHAR, unique=True), schema_extra={'c_required': True})
    email: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True), schema_extra={'c_required': True})
    first_name: str = Field(schema_extra={'c_required': True})
    last_name: str


class UserCreate(BaseUser):
    password: str = Field(schema_extra={'c_required': True})


class User(BaseUser, table=True):
    __tablename__ = "user"
    id: int = Field(primary_key=True)
    hash_pass: str = Field(exclude=True)
    privileges: Privileges
    is_active: bool
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str | None
    media: Optional[List["MediaUser"]] = Relationship(sa_relationship_kwargs={"cascade": "delete"},
                                                      back_populates="user")


class UserResponse(BaseUser):
    id: int = Field(primary_key=True)
    privileges: Privileges
    is_active: bool
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str | None
    media: Optional[List["MediaUser"]]


class UserUpdate(UserCreate):
    old_password: str = Field(schema_extra={'c_required': True})


class UserUpdateAdmin(BaseUser):
    privileges: Privileges = Field(schema_extra={'c_required': True})
    is_active: bool = Field(schema_extra={'c_required': True})


class MediaUserBase(SQLModel):
    media_path: str
    is_main: bool = False


class MediaUser(MediaUserBase, table=True):  # TODO добавить обязательные поля и проверку на них
    __tablename__ = "media_user"
    id: int = Field(primary_key=True)
    user_id: Optional[int] = Field(foreign_key='user.id')
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user: Optional[User] = Relationship(back_populates="media")  # TODO почему не могу заменить на UserResponse?


class MediaUserCreate(MediaUserBase):
    user_id: Optional[int] = Field(foreign_key='user.id')


class MediaUserResponse(MediaUserBase):
    id: int
    created_at: str
    user: Optional[User]  # TODO почему не могу заменить на UserResponse?


User.update_forward_refs()
UserResponse.update_forward_refs()
