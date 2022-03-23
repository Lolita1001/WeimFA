import datetime

from typing import List, Callable
from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.routing import APIRoute

from models.models import DogResponse, DogCreate, BreedCreate, BreedResponse
from db.database import get_session
import db.crud as db
from db.utils.exceptions import HTTPExceptionCustom as HTTPException

api_router = APIRouter()


@api_router.post("/", response_model=DogResponse)
def add_dog(dog_create: DogCreate, session=Depends(get_session)):
    if dog_create.owner_id:
        user_db = db.get_user_by_id(session, dog_create.owner_id)
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect owner_id")
    if dog_create.breeder_id:
        user_db = db.get_user_by_id(session, dog_create.breeder_id)
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect breader_id")
    return db.add_dog(session, dog_create)


@api_router.post("/breed/", response_model=BreedResponse)
def add_breed(breed_create: BreedCreate, session=Depends(get_session)):
    return db.add_breed(session, breed_create)


@api_router.get("/", response_model=List[DogResponse])
def get_dogs(session=Depends(get_session), limit: int = 100, offset: int = 0):
    return db.get_dog_all(session, limit, offset)


@api_router.get("/{dog_id}", response_model=DogResponse)
def get_dog_by_id(dog_id: int, session=Depends(get_session)):
    return db.get_dog_by_id(session, dog_id)


@api_router.delete("/{dog_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_dog_by_id(dog_id: int, session=Depends(get_session)):
    return db.delete_dog_by_id(session, dog_id)
