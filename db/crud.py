from sqlmodel import Session, select
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi import status

from models.models import User, UserCreate, Privileges, UserUpdate,MediaUser, MediaUserCreate
from .secret import get_password_hash, verify_password

from datetime import datetime


def get_user_by_id(session: Session, user_id: int):
    return session.exec(select(User).where(User.id == user_id)).first()


def get_user_all(session: Session, limit: int = 100, offset: int = 0):
    return session.exec(select(User).limit(limit).offset(offset)).all()


def get_user_by_email(session: Session, email: str):
    return session.exec(select(User).where(User.email == email)).first()


def add_user(session: Session, user_create: UserCreate):
    db_user = get_user_by_email(session, user_create.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email must be unique")
    db_user = User(**user_create.dict())
    db_user.hash_pass = get_password_hash(user_create.password)
    db_user.privileges = Privileges.user
    db_user.is_active = True
    db_user.updated_at = None
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session: Session, user_update: UserUpdate):
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


def get_media_user_by_media_id(session: Session, media_id: int):
    return session.exec(select(MediaUser).where(MediaUser.id == media_id)).first()


def get_medias_user_by_user_id(session: Session, user_id: int, limit: int = 100, offset: int = 0):
    return session.exec(select(MediaUser).where(MediaUser.user_id == user_id).limit(limit).offset(offset)).all()


def add_media_user(session: Session, media_user_create: MediaUserCreate):
    db_user = get_user_by_id(session, media_user_create.user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user_id")
    db_media_user = MediaUser(**media_user_create.dict())
    session.add(db_media_user)
    session.commit()
    session.refresh(db_media_user)
    return db_media_user


def delete_media_user(session: Session, media_id: int):
    db_media_user = get_media_user_by_media_id(session, media_id)
    if not db_media_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect media_id")
    session.delete(db_media_user)
    session.commit()
    return JSONResponse({'ok': True})
