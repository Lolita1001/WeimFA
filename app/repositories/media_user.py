from fastapi import status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select

from db.database import get_session, Session
from models.user.schemes import MediaUser
from models.user.validators import MediaUserCreate
from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from repositories.user import UserRepository


class MediaUserRepository(UserRepository):
    def __init__(self, session: Session = Depends(get_session)):
        super(MediaUserRepository, self).__init__()  # TODO не понимаю как это работает, империческом путем получались
        super(UserRepository, self).__init__(session)

    def get_media_user_by_media_id(self, media_id: int) -> MediaUser:
        return self.session.exec(select(MediaUser).where(MediaUser.id == media_id)).first()

    def get_medias_user_by_user_id(self, user_id: int, limit: int = 100, offset: int = 0) -> list[MediaUser]:
        return self.session.exec(select(MediaUser).where(MediaUser.user_id == user_id).limit(limit).offset(offset)).all()

    def add_media_user(self, media_user_create: MediaUserCreate) -> MediaUser:
        db_user = self.get_user_by_id(media_user_create.user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect user_id")
        is_main = self.check_have_main_media(MediaUser)
        db_media_user = MediaUser(**media_user_create.dict())
        db_media_user.is_main = is_main
        self.session.add(db_media_user)
        self.session.commit()
        self.session.refresh(db_media_user)
        return db_media_user

    def delete_media_user(self, media_id: int):
        db_media_user = self.get_media_user_by_media_id(media_id)
        if not db_media_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect media_id")
        self.remove_files(db_media_user.media_path)
        self.session.delete(db_media_user)
        self.session.commit()
        return JSONResponse({'ok': True})
