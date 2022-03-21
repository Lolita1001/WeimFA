from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.sql.expression import Select, SelectOfScalar


SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

SQL_ALCHEMY_DATABASE_URL = "sqlite:///sql_app.db"

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo="debug")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
