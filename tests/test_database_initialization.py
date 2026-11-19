"""Regression checks that never connect to a real database."""

import importlib
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class DatabaseInitializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        environment = patch.dict(os.environ, {
            "DB_NAME": "initialization_test",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "127.0.0.1",
            "DB_PORT": "5432",
            "OPENAI_API_KEY": "test-key",
        })
        environment.start()
        cls.addClassCleanup(environment.stop)

    def test_01_app_import_does_not_connect_or_create_tables(self):
        with (
            patch("sqlalchemy.engine.Engine.connect") as engine_connect,
            patch("sqlalchemy.sql.schema.MetaData.create_all") as create_all,
        ):
            importlib.import_module("api.app")
        engine_connect.assert_not_called()
        create_all.assert_not_called()

    def test_initialization_creates_database_before_registered_tables(self):
        initializer = importlib.import_module("init_db")
        calls = Mock()
        with (
            patch.object(initializer, "create_postgresql_db", calls.database),
            patch.object(initializer.Base.metadata, "create_all", calls.tables),
        ):
            initializer.initialize_database()
        self.assertEqual([call[0] for call in calls.mock_calls], ["database", "tables"])
        calls.tables.assert_called_once_with(bind=initializer.engine)
        self.assertEqual(set(initializer.Base.metadata.tables), {
            "kunden", "kunden_dokumente", "kunden_dokument_positionen",
        })

    def test_initialization_stops_if_database_creation_fails(self):
        initializer = importlib.import_module("init_db")
        with (
            patch.object(initializer, "create_postgresql_db", side_effect=RuntimeError("setup failed")),
            patch.object(initializer.Base.metadata, "create_all") as create_all,
        ):
            with self.assertRaisesRegex(RuntimeError, "setup failed"):
                initializer.initialize_database()
        create_all.assert_not_called()

    def test_database_creation_skips_existing_database_and_closes_connection(self):
        database = importlib.import_module("db.postgresql_db")
        with patch.object(database.psycopg2, "connect") as connect:
            connection = connect.return_value
            cursor = connection.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = (1,)
            database.create_postgresql_db()
        self.assertTrue(connection.autocommit)
        self.assertEqual(cursor.execute.call_count, 1)
        connection.close.assert_called_once()

    def test_database_creation_creates_missing_database(self):
        database = importlib.import_module("db.postgresql_db")
        with patch.object(database.psycopg2, "connect") as connect:
            connection = connect.return_value
            cursor = connection.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = None
            database.create_postgresql_db()
        self.assertTrue(connection.autocommit)
        self.assertEqual(cursor.execute.call_count, 2)
        connection.close.assert_called_once()

    def test_database_creation_propagates_errors_and_closes_connection(self):
        database = importlib.import_module("db.postgresql_db")
        with patch.object(database.psycopg2, "connect") as connect:
            connection = connect.return_value
            cursor = connection.cursor.return_value.__enter__.return_value
            cursor.execute.side_effect = RuntimeError("permission denied")
            with self.assertRaisesRegex(RuntimeError, "permission denied"):
                database.create_postgresql_db()
        connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
