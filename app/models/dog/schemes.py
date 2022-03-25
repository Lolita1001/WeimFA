from datetime import datetime

from typing import Optional, List
from sqlmodel import Field, Relationship

from models.dog.base import BreedBase, DogBase, MediaDogBase, DogAwardBase


class Breed(BreedBase, table=True):
    __tablename__ = "breed"
    id: int = Field(primary_key=True)


class Dog(DogBase, table=True):
    __tablename__ = "dog"
    id: int = Field(primary_key=True)
    breed_id: int = Field(foreign_key='breed.id')
    breed: Breed = Relationship(sa_relationship_kwargs={"foreign_keys": "Dog.breed_id"})
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str | None
    is_approved: bool = False
    approved_id_by: Optional[int] = Field(foreign_key='user.id')
    approved_by: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "Dog.approved_id_by"})
    approved_at: str | None
    owner_id: Optional[int] = Field(foreign_key='user.id')
    breeder_id: Optional[int] = Field(foreign_key='user.id')
    mother_id: Optional[int]
    father_id: Optional[int]
    owner: Optional["User"] = Relationship(back_populates='dog_owner',
                                         sa_relationship_kwargs={"foreign_keys": "[Dog.owner_id]"})
    breeder: Optional["User"] = Relationship(back_populates='dog_breeder',
                                           sa_relationship_kwargs={"foreign_keys": "[Dog.breeder_id]"})
    media: Optional[List["MediaDog"]] = Relationship(sa_relationship_kwargs={"cascade": "delete"},
                                                     back_populates="dog")
    award: Optional[List["DogAward"]] = Relationship(sa_relationship_kwargs={"cascade": "delete"},
                                                     back_populates="dog")


class MediaDog(MediaDogBase, table=True):  # TODO добавить обязательные поля и проверку на них
    __tablename__ = "media_dog"
    id: int = Field(primary_key=True)
    dog_id: Optional[int] = Field(foreign_key='dog.id')
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    dog: Optional["Dog"] = Relationship(back_populates="media")  # TODO почему не могу заменить на DogResponse?


class DogAward(DogAwardBase, table=True):
    __tablename__ = "dog_award"
    id: int = Field(primary_key=True)
    dog_id: int = Field(foreign_key='dog.id')
    dog: Dog = Relationship(back_populates="award")
    is_approved: bool = False
    approved_id_by: Optional[int] = Field(foreign_key='user.id')
    approved_by: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "DogAward.approved_id_by"})
    approved_at: str | None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Dog.update_forward_refs()
