from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.exceptions import HTTPException

from models.models import MediaUserResponse, MediaUserCreate
from db.database import get_session
from db.utils.utils import save_file
import db.crud as db

api_router = APIRouter()


@api_router.get("/{user_id}", response_model=List[MediaUserResponse])  # TODO возврат pass_hash в пользователях
def get_media_user(user_id: int, session=Depends(get_session)):
    return db.get_medias_user_by_user_id(session, user_id)


# @api_router.post("/", response_model=MediaUserResponse)
# def add_media_user(media_user_create: MediaUserCreate, session=Depends(get_session)):
#     return db.add_media_user(session, media_user_create)


@api_router.delete("/{media_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_media_user(media_id: int, session=Depends(get_session)):
    return db.delete_media_user(session, media_id)


@api_router.post("/files/{user_id}", response_model=MediaUserResponse)  # TODO возврат pass_hash в пользователях
def create_file(user_id: int, in_file: UploadFile = File(...), session=Depends(get_session)):
    user_db = db.get_user_by_id(session, user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user_id")
    file_path = save_file(in_file, "static/media_user/")
    if not file_path:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to save file")
    media_user_create = MediaUserCreate(user_id=user_id, media_path=file_path)
    db_media_user = db.add_media_user(session, media_user_create)
    return db_media_user
