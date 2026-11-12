import logging
from contextlib import closing

import psycopg2
from psycopg2 import sql

from core.config import settings

logger = logging.getLogger(__name__)


def create_postgresql_db() -> None:
    """Create the configured database if missing; propagate setup failures."""
    with closing(psycopg2.connect(
        database="postgres",
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )) as conn:
        # CREATE DATABASE must run outside a transaction.
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (settings.DB_NAME,),
            )
            if cursor.fetchone():
                logger.info("Database '%s' already exists.", settings.DB_NAME)
                return

            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(settings.DB_NAME)
                )
            )
            logger.info("Created database '%s'.", settings.DB_NAME)
