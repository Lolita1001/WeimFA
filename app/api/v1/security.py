import datetime

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status

from db.utils.exceptions import HTTPExceptionCustom as HTTPException
from db.secret import verify_password, generate_token, decode_token
from db.database import get_session
import db.crud as db
from models.models import UserResponse

api_router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer("/api/v1/security/token")


@api_router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    db_user = db.get_user_by_email(session, form_data.username)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    if not verify_password(form_data.password, db_user.hash_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    token = generate_token(db_user.email)
    return {"access_token": token, "token_type": "bearer"}


def authentication(token: str = Depends(oauth2_scheme), session=Depends(get_session)):
    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"})
    expiration_date = token_data.get('expiration_date', None)
    if datetime.datetime.fromisoformat(expiration_date) <= datetime.datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"})
    db_user = db.get_user_by_email(session, token_data.get('data', None))  # email from 'data'
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found")
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Account is not active. Email is not confirmed")
    return db_user


@api_router.get("/about_me", response_model=UserResponse)
def about_me(user=Depends(authentication)):
    return user
