from typing import Optional, List
import enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, VARCHAR
from pydantic import EmailStr
from datetime import datetime


class Gender(str, enum.Enum):
    male = "Male"
    female = "Female"


class UserBase(SQLModel):
    login: str = Field(sa_column=Column("login", VARCHAR, unique=True), schema_extra={'c_required': True})
    email: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True), schema_extra={'c_required': True})
    first_name: str = Field(schema_extra={'c_required': True})
    last_name: str


class UserCreate(UserBase):
    password: str = Field(schema_extra={'c_required': True})


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


class UserResponse(UserBase):
    id: int = Field(primary_key=True)
    is_admin: bool
    is_active: bool
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str | None
    media: Optional[List["MediaUser"]]
    dog_owner: Optional[List["Dog"]]
    dog_breeder: Optional[List["Dog"]]


class UserUpdate(UserCreate):
    old_password: str = Field(schema_extra={'c_required': True})


class UserUpdateAdmin(UserBase):
    is_admin: bool = Field(schema_extra={'c_required': True})
    is_active: bool = Field(schema_extra={'c_required': True})


class MediaUserBase(SQLModel):
    media_path: str
    is_main: bool = False


class MediaUser(MediaUserBase, table=True):  # TODO добавить обязательные поля и проверку на них
    __tablename__ = "media_user"
    id: int = Field(primary_key=True)
    user_id: Optional[int] = Field(foreign_key='user.id')
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    user: Optional[User] = Relationship(back_populates="media")  # TODO почему не могу заменить на UserResponse?


class MediaUserCreate(MediaUserBase):
    user_id: Optional[int] = Field(foreign_key='user.id')


class MediaUserResponse(MediaUserBase):
    id: int
    created_at: str
    user: Optional[User]  # TODO почему не могу заменить на UserResponse?


class BreedBase(SQLModel):
    name: str = Field(sa_column=Column("name", VARCHAR, unique=True), schema_extra={'c_required': True})
    description: Optional[str]


class Breed(BreedBase, table=True):
    __tablename__ = "breed"
    id: int = Field(primary_key=True)


class BreedCreate(BreedBase):
    ...


class BreedResponse(Breed):
    ...


class DogBase(SQLModel):
    dog_name_eng: str = Field(schema_extra={'c_required': True})
    dog_name_rus: Optional[str]
    gender: Gender = Field(schema_extra={'c_required': True})
    date_of_birth: str = Field(schema_extra={'c_required': True})
    date_of_death: Optional[str]
    stamp: str = Field(schema_extra={'c_required': True})


class Dog(DogBase, table=True):
    __tablename__ = "dog"
    id: int = Field(primary_key=True)
    breed_id: int = Field(foreign_key='breed.id', schema_extra={'c_required': True})
    breed: Breed = Relationship(sa_relationship_kwargs={"foreign_keys": "Dog.breed_id"})
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str | None
    is_approved: bool = False
    approved_id_by: Optional[int] = Field(foreign_key='user.id')
    approved_by: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "Dog.approved_id_by"})
    approved_at: str | None
    owner_id: Optional[int] = Field(foreign_key='user.id')
    breeder_id: Optional[int] = Field(foreign_key='user.id')
    mother_id: Optional[int]
    father_id: Optional[int]
    owner: Optional[User] = Relationship(back_populates='dog_owner',
                                         sa_relationship_kwargs={"foreign_keys": "[Dog.owner_id]"})
    breeder: Optional[User] = Relationship(back_populates='dog_breeder',
                                           sa_relationship_kwargs={"foreign_keys": "[Dog.breeder_id]"})
    media: Optional[List["MediaDog"]] = Relationship(sa_relationship_kwargs={"cascade": "delete"},
                                                     back_populates="dog")
    award: Optional[List["DogAward"]] = Relationship(sa_relationship_kwargs={"cascade": "delete"},
                                                     back_populates="dog")


class DogResponse(DogBase):
    id: int
    breed: Breed
    owner: Optional[User]
    breeder: Optional[User]
    media: Optional[List["MediaDog"]]
    award: Optional[List["DogAward"]]
    created_at: str
    updated_at: str | None
    is_approved: bool = False
    approved_by: Optional[User]
    approved_at: str | None


class DogCreate(DogBase):
    breed_id: int = Field(foreign_key='breed.id', schema_extra={'c_required': True})
    owner_id: Optional[int]
    breeder_id: Optional[int]
    mother_id: Optional[int]
    father_id: Optional[int]


class MediaDogBase(SQLModel):
    media_path: str
    is_main: bool = False


class MediaDog(MediaDogBase, table=True):  # TODO добавить обязательные поля и проверку на них
    __tablename__ = "media_dog"
    id: int = Field(primary_key=True)
    dog_id: Optional[int] = Field(foreign_key='dog.id')
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    dog: Optional[Dog] = Relationship(back_populates="media")  # TODO почему не могу заменить на DogResponse?


class MediaDogCreate(MediaDogBase):
    dog_id: Optional[int] = Field(foreign_key='dog.id')


class MediaDogResponse(MediaDogBase):
    id: int
    created_at: str
    user: Optional[Dog]  # TODO почему не могу заменить на DogResponse?


class DogAwardBase(SQLModel):
    award: str
    type_award: str


class DogAward(DogAwardBase, table=True):
    __tablename__ = "dog_award"
    id: int = Field(primary_key=True)
    dog_id: int = Field(foreign_key='dog.id')
    dog: Dog = Relationship(back_populates="award")
    is_approved: bool = False
    approved_id_by: Optional[int] = Field(foreign_key='user.id', schema_extra={'c_required': True})
    approved_by: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "DogAward.approved_id_by"})
    approved_at: str | None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DogAwardCreate(DogAwardBase):
    dog_id: int = Field(foreign_key='dog.id')


class DogAwardResponse(DogAwardBase):
    id: int
    dog: Dog
    is_approved: bool
    approved_by: Optional[User]
    approved_at: str | None
    created_at: str


User.update_forward_refs()
UserResponse.update_forward_refs()
Dog.update_forward_refs()
DogResponse.update_forward_refs()
