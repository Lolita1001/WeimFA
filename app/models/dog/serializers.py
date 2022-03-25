from typing import Optional, List

from models.dog.base import DogBase, MediaDogBase, DogAwardBase
from models.dog.schemes import Breed, DogAward, MediaDog, Dog
from models.user.schemes import User


class BreedResponse(Breed):
    ...


class DogResponse(DogBase):
    id: int
    breed: Breed
    owner: Optional["User"]
    breeder: Optional["User"]
    media: Optional[List["MediaDog"]]
    award: Optional[List["DogAward"]]
    created_at: str
    updated_at: str | None
    is_approved: bool = False
    approved_by: Optional["User"]
    approved_at: str | None


class MediaDogResponse(MediaDogBase):
    id: int
    created_at: str
    dog: Optional["Dog"]  # TODO почему не могу заменить на DogResponse?


class DogAwardResponse(DogAwardBase):
    id: int
    dog: "Dog"
    is_approved: bool
    approved_by: Optional["User"]
    approved_at: str | None
    created_at: str


DogResponse.update_forward_refs()
MediaDogResponse.update_forward_refs()
