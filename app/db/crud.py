import os
from datetime import datetime

from sqlmodel import Session, select
from fastapi.responses import JSONResponse
from fastapi import status

from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from models.models import User, UserCreate, UserUpdate
from models.models import MediaUser, MediaUserCreate
from models.models import DogCreate, Dog
from models.models import BreedCreate, Breed
from models.models import MediaDog, MediaDogCreate
from .secret import get_password_hash, verify_password, generate_token


def get_user_by_id(session: Session, user_id: int) -> User:
    return session.exec(select(User).where(User.id == user_id)).first()


def get_user_by_login(session: Session, login: str) -> User:
    return session.exec(select(User).where(User.login == login)).first()


def get_user_all(session: Session, limit: int = 100, offset: int = 0) -> list[User]:
    return session.exec(select(User).limit(limit).offset(offset)).all()


def get_user_by_email(session: Session, email: str) -> User:
    return session.exec(select(User).where(User.email == email)).first()


def add_user(session: Session, user_create: UserCreate) -> User:
    required_field_names, empty_required_fields = check_required_field(user_create)
    if empty_required_fields:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Required fields is empty ({', '.join(empty_required_fields)}). "
                                   f"Required fields: {', '.join(required_field_names)}")
    if get_user_by_email(session, user_create.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email must be unique")
    if get_user_by_login(session, user_create.login):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Login must be unique")
    db_user = User(**user_create.dict())
    db_user.hash_pass = get_password_hash(user_create.password)
    db_user.is_admin = False
    db_user.is_active = False
    db_user.updated_at = None
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    act_token = generate_token(db_user.id)
    # print(act_token)  # TODO токен нужно отправлять на указанную почту.
    # TODO Уточнить процедуру при истечении срока действия токена. Если токен не получен по почте или утерян.
    return db_user, act_token  # TODO для тестов


def update_user(session: Session, user_update: UserUpdate) -> User:
    db_user = get_user_by_email(session, user_update.email)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email")
    if not verify_password(user_update.old_password, db_user.hash_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect password")
    user_update_data = user_update.dict(exclude_unset=True)
    for key, value in user_update_data.items():
        try:
            setattr(db_user, key, value)
        except ValueError as ve:
            if key == "password":
                db_user.hash_pass = get_password_hash(value)
    db_user.updated_at = datetime.utcnow().isoformat()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user_by_id(session: Session, user_id: int):
    db_user = get_user_by_id(session, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user_id")
    path_files = [media.media_path for media in db_user.media]
    remove_files(path_files)
    session.delete(db_user)
    session.commit()
    return JSONResponse({'ok': True})


def get_media_user_by_media_id(session: Session, media_id: int) -> MediaUser:
    return session.exec(select(MediaUser).where(MediaUser.id == media_id)).first()


def get_medias_user_by_user_id(session: Session, user_id: int, limit: int = 100, offset: int = 0) -> list[MediaUser]:
    return session.exec(select(MediaUser).where(MediaUser.user_id == user_id).limit(limit).offset(offset)).all()


def add_media_user(session: Session, media_user_create: MediaUserCreate) -> MediaUser:
    db_user = get_user_by_id(session, media_user_create.user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user_id")
    is_main = check_have_main_media(session, MediaUser)
    db_media_user = MediaUser(**media_user_create.dict())
    db_media_user.is_main = is_main
    session.add(db_media_user)
    session.commit()
    session.refresh(db_media_user)
    return db_media_user


def delete_media_user(session: Session, media_id: int):
    db_media_user = get_media_user_by_media_id(session, media_id)
    if not db_media_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect media_id")
    remove_files(db_media_user.media_path)
    session.delete(db_media_user)
    session.commit()
    return JSONResponse({'ok': True})


def remove_files(path_files: str | list[str]):
    path_files = [path_files] if isinstance(path_files, str) else path_files
    for path_file in path_files:
        if os.path.exists(path_file):
            os.remove(path_file)


def check_required_field(model):
    required_field_names = [field_name for field_name, field_value in model.__fields__.items() if
                            field_value.field_info.extra.get("c_required", False)]
    empty_required_fields = [required_field_name for required_field_name in
                             required_field_names
                             if not model.__getattribute__(required_field_name)]
    return required_field_names, empty_required_fields


def check_have_main_media(session: Session, model):
    db_media = session.exec(select(model).where(model.is_main)).first()
    return False if db_media else True


def get_dog_by_stamp(session: Session, dog_stamp):
    return session.exec(select(Dog).where(Dog.stamp == dog_stamp)).first()


def add_dog(session: Session, dog_create: DogCreate) -> Dog:
    required_field_names, empty_required_fields = check_required_field(dog_create)
    if empty_required_fields:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Required fields is empty ({', '.join(empty_required_fields)}). "
                                   f"Required fields: {', '.join(required_field_names)}")
    if get_dog_by_stamp(session, dog_create.stamp):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Stamp must be unique")
    if not get_breed_by_id(session, dog_create.breed_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Incorrect breed_id")
    db_dog = Dog(**dog_create.dict())
    db_dog.is_approved = False
    session.add(db_dog)
    session.commit()
    session.refresh(db_dog)
    return db_dog


def get_breed_by_name(session: Session, breed_name):
    return session.exec(select(Breed).where(Breed.name == breed_name)).first()


def get_breed_by_id(session: Session, breed_id):
    return session.exec(select(Breed).where(Breed.id == breed_id)).first()


def add_breed(session: Session, breed_create: BreedCreate) -> Breed:
    required_field_names, empty_required_fields = check_required_field(breed_create)
    if empty_required_fields:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Required fields is empty ({', '.join(empty_required_fields)}). "
                                   f"Required fields: {', '.join(required_field_names)}")
    if get_breed_by_name(session, breed_create.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Breed name already exists")
    db_breed = Breed(**breed_create.dict())
    session.add(db_breed)
    session.commit()
    session.refresh(db_breed)
    return db_breed


def get_dog_by_id(session: Session, dog_id) -> Dog:
    return session.exec(select(Dog).where(Dog.id == dog_id)).first()


def get_dog_all(session: Session, limit: int = 100, offset: int = 0) -> list[Dog]:
    return session.exec(select(Dog).limit(limit).offset(offset)).all()


def delete_dog_by_id(session: Session, dog_id: int):
    db_dog = get_dog_by_id(session, dog_id)
    if not db_dog:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect dog_id")
    path_files = [media.media_path for media in db_dog.media]
    remove_files(path_files)
    session.delete(db_dog)
    session.commit()
    return JSONResponse({'ok': True})


def get_media_dog_by_media_id(session: Session, media_id: int) -> MediaDog:
    return session.exec(select(MediaDog).where(MediaDog.id == media_id)).first()


def get_medias_dog_by_dog_id(session: Session, dog_id: int, limit: int = 100, offset: int = 0) -> list[MediaDog]:
    return session.exec(select(MediaDog).where(MediaDog.dog_id == dog_id).limit(limit).offset(offset)).all()


def add_media_dog(session: Session, media_dog_create: MediaDogCreate) -> MediaDog:
    db_dog = get_dog_by_id(session, media_dog_create.dog_id)
    if not db_dog:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect dog_id")
    is_main = check_have_main_media(session, MediaDog)
    db_media_dog = MediaDog(**media_dog_create.dict())
    db_media_dog.is_main = is_main
    session.add(db_media_dog)
    session.commit()
    session.refresh(db_media_dog)
    return db_media_dog


def delete_media_dog(session: Session, media_id: int):
    db_media_dog = get_media_dog_by_media_id(session, media_id)
    if not db_media_dog:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect media_id")
    remove_files(db_media_dog.media_path)
    session.delete(db_media_dog)
    session.commit()
    return JSONResponse({'ok': True})

