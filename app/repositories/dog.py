from fastapi import status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select

from db.database import get_session, Session
from models.dog.schemes import Dog, Breed
from models.dog.validators import DogCreate, BreedCreate
from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from repositories.user import UserRepository


class DogRepository(UserRepository):
    def __init__(self, session: Session = Depends(get_session)):
        super(DogRepository, self).__init__()  # TODO не понимаю как это работает, империческом путем получались
        super(UserRepository, self).__init__(session)

    def get_dog_by_stamp(self, dog_stamp):
        return self.session.exec(select(Dog).where(Dog.stamp == dog_stamp)).first()

    def add_dog(self, dog_create: DogCreate) -> Dog:
        required_field_names, empty_required_fields = self.check_required_field(dog_create)
        if empty_required_fields:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Required fields is empty ({', '.join(empty_required_fields)}). "
                                       f"Required fields: {', '.join(required_field_names)}")
        if self.get_dog_by_stamp(dog_create.stamp):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Stamp must be unique")
        if not self.get_breed_by_id(dog_create.breed_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Incorrect breed_id")
        db_dog = Dog(**dog_create.dict())
        db_dog.is_approved = False
        self.session.add(db_dog)
        self.session.commit()
        self.session.refresh(db_dog)
        return db_dog

    def get_breed_by_name(self, breed_name):
        return self.session.exec(select(Breed).where(Breed.name == breed_name)).first()

    def get_breed_by_id(self, breed_id):
        return self.session.exec(select(Breed).where(Breed.id == breed_id)).first()

    def add_breed(self, breed_create: BreedCreate) -> Breed:
        required_field_names, empty_required_fields = self.check_required_field(breed_create)
        if empty_required_fields:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Required fields is empty ({', '.join(empty_required_fields)}). "
                                       f"Required fields: {', '.join(required_field_names)}")
        if self.get_breed_by_name(breed_create.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Breed name already exists")
        db_breed = Breed(**breed_create.dict())
        self.session.add(db_breed)
        self.session.commit()
        self.session.refresh(db_breed)
        return db_breed

    def get_dog_by_id(self, dog_id) -> Dog:
        return self.session.exec(select(Dog).where(Dog.id == dog_id)).first()

    def get_dog_all(self, limit: int = 100, offset: int = 0) -> list[Dog]:
        return self.session.exec(select(Dog).limit(limit).offset(offset)).all()

    def delete_dog_by_id(self, dog_id: int):
        db_dog = self.get_dog_by_id(dog_id)
        if not db_dog:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect dog_id")
        path_files = [media.media_path for media in db_dog.media]
        self.remove_files(path_files)  # TODO при удалении пользователя, удаляются все его собаки, но не удаляются файлы
        self.session.delete(db_dog)
        self.session.commit()
        return JSONResponse({'ok': True})
