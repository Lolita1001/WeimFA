from typing import List, Callable

from fastapi import APIRouter, Depends, status, Response, Request, File, UploadFile
from fastapi.routing import APIRoute

from models.user.validators import UserUpdate, UserCreate
from models.user.serializers import UserResponse
from models.user.validators import MediaUserCreate
from models.user.serializers import MediaUserResponse
from repositories.media_user import MediaUserRepository
from repositories.user import UserRepository
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


@api_router.get("/media/{user_id}", response_model=List[MediaUserResponse])
def get_media_user(user_id: int, repository: MediaUserRepository = Depends(MediaUserRepository)):
    return repository.get_medias_user_by_user_id(user_id)


@api_router.delete("/media/{media_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_media_user(media_id: int, repository: MediaUserRepository = Depends(MediaUserRepository)):
    return repository.delete_media_user(media_id)


@api_router.post("/media/{user_id}", response_model=MediaUserResponse)
def create_file(user_id: int, in_file: UploadFile = File(...), repository: MediaUserRepository = Depends(MediaUserRepository)):
    user_db = repository.get_user_by_id(user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user_id")
    file_path = repository.save_file(in_file, "static/media_user/")
    media_user_create = MediaUserCreate(user_id=user_id, media_path=file_path)
    db_media_user = repository.add_media_user(media_user_create)
    return db_media_user
