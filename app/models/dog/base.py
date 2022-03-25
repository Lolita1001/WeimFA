from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, VARCHAR


class Gender(str, Enum):
    male = "Male"
    female = "Female"


class DogBase(SQLModel):
    dog_name_eng: str = Field(schema_extra={'c_required': True})
    dog_name_rus: Optional[str]
    gender: Gender = Field(schema_extra={'c_required': True})
    date_of_birth: str = Field(schema_extra={'c_required': True})
    date_of_death: Optional[str]
    stamp: str = Field(schema_extra={'c_required': True})


class BreedBase(SQLModel):
    name: str = Field(sa_column=Column("name", VARCHAR, unique=True), schema_extra={'c_required': True})
    description: Optional[str]


class MediaDogBase(SQLModel):
    media_path: str
    is_main: bool = False


class DogAwardBase(SQLModel):
    award: str
    type_award: str
