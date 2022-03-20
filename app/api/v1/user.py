from typing import List
from fastapi import APIRouter, Depends, status

from models.models import UserResponse, UserCreate, UserUpdate
from db.database import get_session
import db.crud as db

api_router = APIRouter()


@api_router.post("/", response_model=UserResponse)
def add_user(user_create: UserCreate, session=Depends(get_session)):
    return db.add_user(session, user_create)


@api_router.get("/{user_id_or_email}", response_model=UserResponse)
def get_user_by_id_or_email(user_id_or_email: int | str, session=Depends(get_session)):
    match user_id_or_email:
        case int(): return db.get_user_by_id(session, user_id_or_email)
        case str(): return db.get_user_by_email(session, user_id_or_email)


@api_router.get("/", response_model=List[UserResponse])
def get_users(session=Depends(get_session), limit: int = 100, offset: int = 0):
    return db.get_user_all(session, limit, offset)


@api_router.put("/", response_model=UserResponse)
def update_user(user_update: UserUpdate, session=Depends(get_session)):
    return db.update_user(session, user_update)


@api_router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_user_by_id(user_id: int, session=Depends(get_session)):
    return db.delete_user_by_id(session, user_id)
