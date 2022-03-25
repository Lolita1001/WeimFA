from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile

from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from models.models import MediaDogResponse, MediaDogCreate
from repositories.media_dog import MediaDogRepository

api_router = APIRouter()


@api_router.get("/{dog_id}", response_model=List[MediaDogResponse])
def get_media_dog(dog_id: int, repository: MediaDogRepository = Depends(MediaDogRepository)):
    return repository.get_medias_dog_by_dog_id(dog_id)


@api_router.delete("/{media_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_media_dog(media_id: int, repository: MediaDogRepository = Depends(MediaDogRepository)):
    return repository.delete_media_dog(media_id)


@api_router.post("/{dog_id}", response_model=MediaDogResponse)
def create_file(dog_id: int, in_file: UploadFile = File(...), repository: MediaDogRepository = Depends(MediaDogRepository)):
    dog_db = repository.get_dog_by_id(dog_id)
    if not dog_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect dog_id")
    file_path = repository.save_file(in_file, "static/media_dog/")
    media_dog_create = MediaDogCreate(dog_id=dog_id, media_path=file_path)
    db_media_dog = repository.add_media_dog(media_dog_create)
    return db_media_dog
