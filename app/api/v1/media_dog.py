from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile

from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from models.models import MediaDogResponse, MediaDogCreate
from db.database import get_session
from db.utils.utils import save_file
import db.crud as db

api_router = APIRouter()


@api_router.get("/{dog_id}", response_model=List[MediaDogResponse])
def get_media_dog(dog_id: int, session=Depends(get_session)):
    return db.get_medias_dog_by_dog_id(session, dog_id)


@api_router.delete("/{media_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_media_dog(media_id: int, session=Depends(get_session)):
    return db.delete_media_dog(session, media_id)


@api_router.post("/{dog_id}", response_model=MediaDogResponse)
def create_file(dog_id: int, in_file: UploadFile = File(...), session=Depends(get_session)):
    dog_db = db.get_dog_by_id(session, dog_id)
    if not dog_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect dog_id")
    file_path = save_file(in_file, "static/media_dog/")
    media_dog_create = MediaDogCreate(dog_id=dog_id, media_path=file_path)
    db_media_dog = db.add_media_dog(session, media_dog_create)
    return db_media_dog
