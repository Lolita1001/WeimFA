from typing import Optional

from sqlmodel import Field

from models.dog.base import BreedBase, DogBase, MediaDogBase, DogAwardBase


class BreedCreate(BreedBase):
    ...


class DogCreate(DogBase):
    breed_id: int = Field(schema_extra={'c_required': True})
    owner_id: Optional[int]
    breeder_id: Optional[int]
    mother_id: Optional[int]
    father_id: Optional[int]


class MediaDogCreate(MediaDogBase):
    dog_id: Optional[int]


class DogAwardCreate(DogAwardBase):
    dog_id: int = Field(schema_extra={'c_required': True})
