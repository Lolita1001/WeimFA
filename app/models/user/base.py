from sqlmodel import SQLModel, Field
from sqlalchemy import Column, VARCHAR
from pydantic import EmailStr


class UserBase(SQLModel):
    login: str = Field(sa_column=Column("login", VARCHAR, unique=True), schema_extra={'c_required': True})
    email: EmailStr = Field(sa_column=Column("email", VARCHAR, unique=True), schema_extra={'c_required': True})
    first_name: str = Field(schema_extra={'c_required': True})
    last_name: str


class MediaUserBase(SQLModel):
    media_path: str
    is_main: bool = False
