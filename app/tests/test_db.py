from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.sql.expression import Select, SelectOfScalar
import os.path

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

SQL_ALCHEMY_DATABASE_URL = "sqlite:///test_sql_app.db"

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

if os.path.exists("test_sql_app.db"):
    os.remove("test_sql_app.db")

SQLModel.metadata.create_all(engine)


def override_get_session():
    with Session(engine) as session:
        yield session
