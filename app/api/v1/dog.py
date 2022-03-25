from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile

from models.dog.serializers import DogResponse, BreedResponse
from models.dog.validators import DogCreate, BreedCreate
from models.dog.validators import MediaDogCreate
from models.dog.serializers import MediaDogResponse
from repositories.media_dog import MediaDogRepository
from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from repositories.dog import DogRepository

api_router = APIRouter()


@api_router.post("/", response_model=DogResponse)
def add_dog(dog_create: DogCreate, repository: DogRepository = Depends(DogRepository)):
    if dog_create.owner_id:
        user_db = repository.get_user_by_id(dog_create.owner_id)
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect owner_id")
    if dog_create.breeder_id:
        user_db = repository.get_user_by_id(dog_create.breeder_id)
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect breader_id")
    return repository.add_dog(dog_create)


@api_router.post("/breed/", response_model=BreedResponse)
def add_breed(breed_create: BreedCreate, repository: DogRepository = Depends(DogRepository)):
    return repository.add_breed(breed_create)


@api_router.get("/", response_model=List[DogResponse])
def get_dogs(limit: int = 100, offset: int = 0, repository: DogRepository = Depends(DogRepository)):
    return repository.get_dog_all(limit, offset)


@api_router.get("/{dog_id}", response_model=DogResponse)
def get_dog_by_id(dog_id: int, repository: DogRepository = Depends(DogRepository)):
    return repository.get_dog_by_id(dog_id)


@api_router.delete("/{dog_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_dog_by_id(dog_id: int, repository: DogRepository = Depends(DogRepository)):
    return repository.delete_dog_by_id(dog_id)


@api_router.get("/media/{dog_id}", response_model=List[MediaDogResponse])
def get_media_dog(dog_id: int, repository: MediaDogRepository = Depends(MediaDogRepository)):
    return repository.get_medias_dog_by_dog_id(dog_id)


@api_router.delete("/media/{media_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_media_dog(media_id: int, repository: MediaDogRepository = Depends(MediaDogRepository)):
    return repository.delete_media_dog(media_id)


@api_router.post("/media/{dog_id}", response_model=MediaDogResponse)
def create_file(dog_id: int, in_file: UploadFile = File(...), repository: MediaDogRepository = Depends(MediaDogRepository)):
    dog_db = repository.get_dog_by_id(dog_id)
    if not dog_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect dog_id")
    file_path = repository.save_file(in_file, "static/media_dog/")
    media_dog_create = MediaDogCreate(dog_id=dog_id, media_path=file_path)
    db_media_dog = repository.add_media_dog(media_dog_create)
    return db_media_dog
