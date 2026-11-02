from contextlib import contextmanager
from collections.abc import Generator
from sqlmodel import SQLModel, create_engine, Session

from multi_agent_system.config import settings


DATABASE_URL = f"sqlite:///{settings.db_path}"


engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    """
    Erstellt alle SQLModel-Tabellen.
    """
    # Models importieren, damit SQLModel.metadata die Tabellen kennt.
    from multi_agent_system.database.models import (
        Kunde,
        KundenDokument,
        KundenDokumentPosition,
        FirmenDokument,
        FirmenDokumentPosition,
    )
    SQLModel.metadata.create_all(engine)


# @contextmanager
# def session_scope() -> Generator[Session, None, None]:
#     with Session(engine) as session:
#         yield session

@contextmanager
def session_scope() -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI Dependency.
    """
    with Session(engine) as session:
        yield session