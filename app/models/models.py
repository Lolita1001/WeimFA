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
    login: str = Field(sa_column=Column("login", VARCHAR, unique=True))
    email: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True))
    full_name: str


class UserCreate(BaseUser):
    password: str


class User(BaseUser, table=True):
    __tablename__ = "users"
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
    old_password: str


class UserUpdateAdmin(BaseUser):  # TODO How should the administrator change the privileges of other users
    privileges: Privileges
    is_active: bool


class MediaUserBase(SQLModel):
    media_path: str


class MediaUser(MediaUserBase, table=True):
    __tablename__ = "media_users"
    id: int = Field(primary_key=True)
    user_id: Optional[int] = Field(foreign_key='users.id')
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user: Optional[User] = Relationship(back_populates="media")  # TODO почему не могу заменить на UserResponse?


class MediaUserCreate(MediaUserBase):
    user_id: Optional[int] = Field(foreign_key='users.id')


class MediaUserResponse(MediaUserBase):
    id: int
    created_at: str
    user: Optional[User]  # TODO почему не могу заменить на UserResponse?


User.update_forward_refs()
UserResponse.update_forward_refs()
