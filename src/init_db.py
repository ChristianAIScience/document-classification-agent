"""Initialize PostgreSQL explicitly: uv run python src/init_db.py."""

import logging

import db.models  # Register all models in Base.metadata before creating tables.
from db.database import Base, engine
from db.postgresql_db import create_postgresql_db

logger = logging.getLogger(__name__)


def initialize_database() -> None:
    """Create the database and missing tables without changing existing tables."""
    create_postgresql_db()
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
    initialize_database()
