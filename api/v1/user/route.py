from typing import List
from fastapi import APIRouter, Depends

from models.models import UserResponse, UserCreate, UserUpdate
from db.database import get_session
import db.crud as db

api_router = APIRouter()


@api_router.post("/", response_model=UserResponse)
def add_user(user_create: UserCreate, session=Depends(get_session)):
    return db.add_user(session, user_create)


@api_router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, session=Depends(get_session)):
    return db.get_user_by_id(session, user_id)


@api_router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email(email: str, session=Depends(get_session)):
    return db.get_user_by_email(session, email)


@api_router.get("/", response_model=List[UserResponse])
def get_users(session=Depends(get_session)):  # TODO add limit and offset
    return db.get_user_all(session)


@api_router.put("/", response_model=UserResponse)
def update_user(user_update: UserUpdate, session=Depends(get_session)):
    return db.update_user(session, user_update)
