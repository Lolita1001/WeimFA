from datetime import datetime

from fastapi import status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select

from db.database import get_session, Session
from repositories.base import BaseRepository
from repositories.security import SecurityRepository
from models.models import User, UserCreate, UserUpdate
from db.utils.exceptions import HTTPExceptionCustom as HTTPException


class UserRepository(BaseRepository, SecurityRepository):
    def __init__(self, session: Session = Depends(get_session)):
        super(UserRepository, self).__init__(session)  # TODO не понимаю как это работает, империческом путем получались
        super(BaseRepository, self).__init__()

    def get_user_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        return self.session.exec(select(User).limit(limit).offset(offset)).all()

    def get_user_by_id(self, user_id: int) -> User:
        return self.session.exec(select(User).where(User.id == user_id)).first()

    def get_user_by_login(self, login: str) -> User:
        return self.session.exec(select(User).where(User.login == login)).first()

    def get_user_by_email(self, email: str) -> User:
        return self.session.exec(select(User).where(User.email == email)).first()

    def add_user(self, user_create: UserCreate) -> User:
        required_field_names, empty_required_fields = self.check_required_field(user_create)
        if empty_required_fields:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Required fields is empty ({', '.join(empty_required_fields)}). "
                                       f"Required fields: {', '.join(required_field_names)}")
        if self.get_user_by_email(user_create.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Email must be unique")
        if self.get_user_by_login(user_create.login):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Login must be unique")
        db_user = User(**user_create.dict())
        db_user.hash_pass = self.get_password_hash(user_create.password)
        db_user.is_admin = False
        db_user.is_active = False
        db_user.updated_at = None
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        act_token = self.generate_token(db_user.id)
        # print(act_token)  # TODO токен нужно отправлять на указанную почту.
        # TODO Уточнить процедуру при истечении срока действия токена. Если токен не получен по почте или утерян.
        return db_user, act_token  # TODO для тестов

    def update_user(self, user_update: UserUpdate) -> User:
        db_user = self.get_user_by_email(user_update.email)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect email")
        if not self.verify_password(user_update.old_password, db_user.hash_pass):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect password")
        user_update_data = user_update.dict(exclude_unset=True)
        for key, value in user_update_data.items():
            try:
                setattr(db_user, key, value)
            except ValueError as ve:
                if key == "password":
                    db_user.hash_pass = self.get_password_hash(value)
        db_user.updated_at = datetime.utcnow().isoformat()
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def delete_user_by_id(self, user_id: int) -> JSONResponse:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect user_id")
        path_files = [media.media_path for media in db_user.media]
        self.remove_files(path_files)
        self.session.delete(db_user)
        self.session.commit()
        return JSONResponse({'ok': True})

    def activate_user(self, activate_token: str) -> User:
        token_data = self.decode_token(activate_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials")
        expiration_date = token_data.get('expiration_date', None)
        if datetime.fromisoformat(expiration_date) <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials")
        db_user = self.get_user_by_id(token_data.get('data', None))  # user_id from 'data'
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found")
        db_user.is_active = True
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
