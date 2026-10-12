

from contextlib import contextmanager
from collections.abc import Generator

from sqlmodel import SQLModel, Session, create_engine

from multi_agent_system.config import settings


DATABASE_URL = (f"postgresql+psycopg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}")


engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def create_db_and_tables() -> None:
    """
    Erstellt alle SQLModel-Tabellen.
    """

    # Wichtig:
    # Models müssen importiert sein, damit sie in SQLModel.metadata
    # registriert werden.
    from multi_agent_system.database.models import (
        Kunde,
        KundenDokument,
        KundenDokumentPosition,
        FirmenDokument,
        FirmenDokumentPosition,
    )

    SQLModel.metadata.create_all(engine)
    
# Beispiel für eine Session (bleibt ebenfalls 100% identisch)
def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    print("Verbinde mit Datenbank und ertestelle Tabellen...")
    create_db_and_tables()
    print("Fertig!")

# @contextmanager
# def session_scope() -> Generator[Session, None, None]:
#     with Session(engine) as session:
#         try:
#             yield session
#             session.commit()
#         except Exception:
#             session.rollback()
#             raise


# def get_session() -> Generator[Session, None, None]:
#     with Session(engine) as session:
#         yield session