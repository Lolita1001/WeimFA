from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.sql.expression import Select, SelectOfScalar
from fastapi.exceptions import HTTPException
import sys


SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

SQL_ALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        try:
            yield session
        except Exception as ex:
            session.close()
            # type, value, traceback = sys.exc_info()
            # raise HTTPException(
            #     status_code=403,
            #     detail=str(value.orig))
