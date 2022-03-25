from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile

from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from models.models import MediaUserResponse, MediaUserCreate
from repositories.media_user import MediaUserRepository

api_router = APIRouter()


@api_router.get("/{user_id}", response_model=List[MediaUserResponse])
def get_media_user(user_id: int, repository: MediaUserRepository = Depends(MediaUserRepository)):
    return repository.get_medias_user_by_user_id(user_id)


@api_router.delete("/{media_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_media_user(media_id: int, repository: MediaUserRepository = Depends(MediaUserRepository)):
    return repository.delete_media_user(media_id)


@api_router.post("/{user_id}", response_model=MediaUserResponse)
def create_file(user_id: int, in_file: UploadFile = File(...), repository: MediaUserRepository = Depends(MediaUserRepository)):
    user_db = repository.get_user_by_id(user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user_id")
    file_path = repository.save_file(in_file, "static/media_user/")
    media_user_create = MediaUserCreate(user_id=user_id, media_path=file_path)
    db_media_user = repository.add_media_user(media_user_create)
    return db_media_user
