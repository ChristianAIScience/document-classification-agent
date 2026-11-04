from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from db.postgresql_db import create_postgresql_db
from core.config import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./testing.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
# )

create_postgresql_db()  # Ensure the PostgreSQL database is created before proceeding

DATABASE_URL = (
    f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db
