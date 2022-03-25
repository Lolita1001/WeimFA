from datetime import datetime

from typing import Optional, List
from sqlmodel import Field, Relationship

from models.user.base import UserBase, MediaUserBase


class User(UserBase, table=True):
    __tablename__ = "user"
    id: int = Field(primary_key=True)
    hash_pass: str = Field(exclude=True)
    is_admin: bool
    is_active: bool
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str | None
    media: Optional[List["MediaUser"]] = Relationship(sa_relationship_kwargs={"cascade": "delete"},
                                                      back_populates="user")
    dog_owner: Optional[List["Dog"]] = Relationship(sa_relationship_kwargs={"cascade": "delete",
                                                                            "foreign_keys": "[Dog.owner_id]"},
                                                    back_populates='owner')
    dog_breeder: Optional[List["Dog"]] = Relationship(sa_relationship_kwargs={"cascade": "delete",
                                                                              "foreign_keys": "[Dog.breeder_id]"},
                                                      back_populates='breeder')


class MediaUser(MediaUserBase, table=True):  # TODO добавить обязательные поля и проверку на них
    __tablename__ = "media_user"
    id: int = Field(primary_key=True)
    user_id: Optional[int] = Field(foreign_key='user.id')
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    user: Optional["User"] = Relationship(back_populates="media")  # TODO почему не могу заменить на UserResponse?


# User.update_forward_refs()
