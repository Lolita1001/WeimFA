import datetime

from typing import List
from fastapi import APIRouter, Depends, status

from models.models import UserResponse, UserCreate, UserUpdate
from db.database import get_session
import db.crud as db
from db.secret import decode_token
from db.utils.exceptions import HTTPExceptionCustom as HTTPException

api_router = APIRouter()


@api_router.post("/", response_model=UserResponse)
def add_user(user_create: UserCreate, session=Depends(get_session)):
    return db.add_user(session, user_create)


@api_router.post("/activate/{activate_token}", status_code=status.HTTP_202_ACCEPTED)
def activate_user(activate_token: str, session=Depends(get_session)):
    token_data = decode_token(activate_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials")
    expiration_date = token_data.get('expiration_date', None)
    if datetime.datetime.fromisoformat(expiration_date) <= datetime.datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials")
    db_user = db.get_user_by_id(session, token_data.get('activate_user_id', None))
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found")
    db_user.is_active = True
    session.add(db_user)
    session.commit()
    session.refresh(db_user)


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
