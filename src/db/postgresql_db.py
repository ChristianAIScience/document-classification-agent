import logging
import psycopg2
from psycopg2 import sql
from core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)


def create_postgresql_db() -> None:
    """
    Create a PostgreSQL database if it does not exist.
    """
    logger.info("--- 🔧 🚀 Überpüfe, ob die Datenbank existiert. ---")
    try:
        # 1. Verbindung zur Standard-Datenbank "postgres" herstellen,
        # da die Zieldatenbank eventuell noch nicht existiert!
        conn = psycopg2.connect(
            database="postgres",
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        db_name = settings.DB_NAME

        # 2. Prüfen, ob die Datenbank bereits existiert
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if exists:
            logger.info(f"--- 🤖 Die Datenbank '{db_name}' existiert bereits. ---")
        else:
            # 3. Datenbank erstellen 
            # (psycopg2.sql.Identifier schützt sicher vor SQL-Injections bei Namen)
            query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
            cursor.execute(query)
            logger.info(f"--- ✅ Die Datenbank '{db_name}' wurde erfolgreich erstellt! ---")

        # Aufräumen
        cursor.close()
        conn.close()

    except Exception as error:
        logger.error(f"--- ❌ Beim Erstellen der Datenbank '{db_name}' ist ein Fehler aufgetreten: {error}")