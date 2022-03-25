from fastapi import status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select

from db.database import get_session, Session
from models.dog.schemes import MediaDog
from models.dog.validators import MediaDogCreate
from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from repositories.dog import DogRepository


class MediaDogRepository(DogRepository):
    def __init__(self, session: Session = Depends(get_session)):
        super(MediaDogRepository, self).__init__()  # TODO не понимаю как это работает, империческом путем получались
        super(DogRepository, self).__init__(session)

    def get_media_dog_by_media_id(self, media_id: int) -> MediaDog:
        return self.session.exec(select(MediaDog).where(MediaDog.id == media_id)).first()

    def get_medias_dog_by_dog_id(self, dog_id: int, limit: int = 100, offset: int = 0) -> list[MediaDog]:
        return self.session.exec(select(MediaDog).where(MediaDog.dog_id == dog_id).limit(limit).offset(offset)).all()

    def add_media_dog(self, media_dog_create: MediaDogCreate) -> MediaDog:
        db_dog = self.get_dog_by_id(media_dog_create.dog_id)
        if not db_dog:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect dog_id")
        is_main = self.check_have_main_media(MediaDog)
        db_media_dog = MediaDog(**media_dog_create.dict())
        db_media_dog.is_main = is_main
        self.session.add(db_media_dog)
        self.session.commit()
        self.session.refresh(db_media_dog)
        return db_media_dog

    def delete_media_dog(self, media_id: int):
        db_media_dog = self.get_media_dog_by_media_id(media_id)
        if not db_media_dog:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect media_id")
        self.remove_files(db_media_dog.media_path)
        self.session.delete(db_media_dog)
        self.session.commit()
        return JSONResponse({'ok': True})
