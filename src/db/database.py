from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from core.config import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./testing.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
# )

DATABASE_URL = (
    f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db

# 5. Dependency-Funktion für FastAPI, um eine Session zu injizieren
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()