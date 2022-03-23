import datetime

from typing import List, Callable
from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.routing import APIRoute

from models.models import UserResponse, UserCreate, UserUpdate
from db.database import get_session
import db.crud as db
from db.secret import decode_token
from db.utils.exceptions import HTTPExceptionCustom as HTTPException


class LoggingRoute(APIRoute):  # TODO сделать логер
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            return response
        return custom_route_handler


api_router = APIRouter(route_class=LoggingRoute)


@api_router.post("/", response_model=UserResponse)
def add_user(user_create: UserCreate, res: Response, session=Depends(get_session)):
    db_user, act_token = db.add_user(session, user_create)
    if user_create.email.split('@')[1] == 'example.com':  # TODO удалить, другого способа не придумал. Для тестов
        res.headers['act_token'] = act_token
    return db_user


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
    db_user = db.get_user_by_id(session, token_data.get('data', None))  # user_id from 'data'
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
