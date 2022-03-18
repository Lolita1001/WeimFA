from typing import List
from fastapi import APIRouter, Depends, status

from models.models import MediaUserResponse, MediaUserCreate
from db.database import get_session
import db.crud as db

api_router = APIRouter()


@api_router.get("/media_user/{user_id}", response_model=List[MediaUserResponse])
def get_media_user(user_id: int, session=Depends(get_session)):
    return db.get_medias_user_by_user_id(session, user_id)


@api_router.post("/media_user", response_model=MediaUserResponse)
def add_media_user(media_user_create: MediaUserCreate, session=Depends(get_session)):
    return db.add_media_user(session, media_user_create)


@api_router.delete("/media_user/{media_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_media_user(media_id: int, session=Depends(get_session)):
    return db.delete_media_user(session, media_id)
