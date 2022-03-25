from typing import List, Callable

from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.routing import APIRoute

from models.models import UserResponse, UserCreate, UserUpdate
from repositories.user import UserRepository


class LoggingRoute(APIRoute):  # TODO сделать логер
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            return response
        return custom_route_handler


api_router = APIRouter(route_class=LoggingRoute)


@api_router.post("/", response_model=UserResponse)
def add_user(user_create: UserCreate, response: Response, repository: UserRepository = Depends(UserRepository)):
    db_user, act_token = repository.add_user(user_create)
    if user_create.email.split('@')[1] == 'example.com':  # TODO удалить, другого способа не придумал. Для тестов
        response.headers['act_token'] = act_token
    return db_user


@api_router.post("/activate/{activate_token}", status_code=status.HTTP_202_ACCEPTED, response_model=UserResponse)
def activate_user(activate_token: str, repository: UserRepository = Depends(UserRepository)):
    return repository.activate_user(activate_token)


@api_router.get("/{user_id_or_email}", response_model=UserResponse)
def get_user_by_id_or_email(user_id_or_email: int | str, repository: UserRepository = Depends(UserRepository)):
    match user_id_or_email:
        case int(): return repository.get_user_by_id(user_id_or_email)
        case str(): return repository.get_user_by_email(user_id_or_email)


@api_router.get("/", response_model=List[UserResponse])
def get_users(limit: int = 100, offset: int = 0, repository: UserRepository = Depends(UserRepository)):
    return repository.get_user_all(limit, offset)


@api_router.put("/", response_model=UserResponse)
def update_user(user_update: UserUpdate, repository: UserRepository = Depends(UserRepository)):
    return repository.update_user(user_update)


@api_router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_user_by_id(user_id: int, repository: UserRepository = Depends(UserRepository)):
    return repository.delete_user_by_id(user_id)
