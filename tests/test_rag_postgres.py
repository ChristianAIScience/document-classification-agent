"""Opt-in real pgvector checks: set TEST_RAG_DATABASE_URL to a test PostgreSQL DB."""

import os
from pathlib import Path
import sys
import unittest
from uuid import uuid4

from langchain_core.embeddings import DeterministicFakeEmbedding
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag.config import RagSettings
from rag.service import RagService
from rag.setup import initialize_vector_store
from rag.vector_store import open_vector_store


@unittest.skipUnless(os.getenv("TEST_RAG_DATABASE_URL"), "TEST_RAG_DATABASE_URL is not configured")
class PostgresRagTests(unittest.IsolatedAsyncioTestCase):
    async def test_initialize_upsert_filter_search_and_delete(self):
        engine = create_engine(os.environ["TEST_RAG_DATABASE_URL"])
        self.addCleanup(engine.dispose)
        config = RagSettings(
            _env_file=None, table_name=f"rag_test_{uuid4().hex}", embedding_dimensions=8,
        )

        def remove_test_table():
            with engine.begin() as connection:
                connection.execute(text(f'DROP TABLE IF EXISTS public."{config.table_name}"'))

        self.addCleanup(remove_test_table)
        initialize_vector_store(engine, config)
        initialize_vector_store(engine, config)
        async with open_vector_store(DeterministicFakeEmbedding(size=8), engine.url, config) as store:
            service = RagService(store, config)
            ids = await service.add_text("Montage", source="angebot.pdf", metadata={"kunde_id": 7})
            self.assertEqual(ids, await service.add_text("Montage", source="angebot.pdf", metadata={"kunde_id": 7}))
            await service.add_text("Montage", source="anderes.pdf", metadata={"kunde_id": 8})
            matches = await service.search("Montage", filters={"kunde_id": {"$eq": 7}})
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].metadata["source"], "angebot.pdf")
            self.assertTrue(await service.delete_chunks(ids))
            self.assertEqual(await service.search("Montage", filters={"kunde_id": {"$eq": 7}}), [])


if __name__ == "__main__":
    unittest.main()
