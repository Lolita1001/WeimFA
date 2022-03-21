import os

from sqlmodel import Session, select
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi import status

from models.models import User, UserCreate, Privileges, UserUpdate, MediaUser, MediaUserCreate
from .secret import get_password_hash, verify_password

from datetime import datetime


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
    db_user.privileges = Privileges.user
    db_user.is_active = True
    db_user.updated_at = None
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


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
    db_user.updated_at = datetime.now().isoformat()
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
