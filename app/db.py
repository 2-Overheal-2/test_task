import os

from sqlmodel import create_engine, SQLModel, Session

# engine = create_engine("postgresql+psycopg2://app_user:app_password@db:5432/test", echo=False)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Переменная окружения DATABASE_URL не установлена")

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
