"""Offline RAG checks using fake embeddings and isolated vector-store boundaries."""

import importlib
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag.config import RagSettings
from rag.service import RagService
from rag.setup import initialize_vector_store
from rag.vector_store import open_vector_store


class RagConfigurationTests(unittest.TestCase):
    def test_invalid_identifiers_dimensions_and_chunk_settings_are_rejected(self):
        for values in (
            {"table_name": 'chunks"; DROP TABLE kunden; --'},
            {"embedding_dimensions": 0}, {"chunk_overlap": -1},
            {"chunk_size": 150, "chunk_overlap": 150}, {"search_k": 0},
        ):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                RagSettings(_env_file=None, **values)

    def test_setup_creates_missing_objects_without_overwriting_tables(self):
        engine = MagicMock()
        connection = engine.begin.return_value.__enter__.return_value
        connection.execute.return_value.scalar_one.return_value = "vector(8)"
        initialize_vector_store(engine, RagSettings(_env_file=None, embedding_dimensions=8))
        statements = [str(call.args[0]) for call in connection.execute.call_args_list]
        self.assertIn("CREATE EXTENSION IF NOT EXISTS vector", statements[0])
        self.assertIn('CREATE TABLE IF NOT EXISTS public."rag_document_chunks"', statements[1])
        self.assertIn("vector(8)", statements[1])
        self.assertTrue(all("DROP" not in statement for statement in statements))

    def test_setup_rejects_existing_table_with_different_dimensions(self):
        engine = MagicMock()
        engine.begin.return_value.__enter__.return_value.execute.return_value.scalar_one.return_value = "vector(16)"
        with self.assertRaisesRegex(ValueError, "expected vector\\(8\\)"):
            initialize_vector_store(engine, RagSettings(_env_file=None, embedding_dimensions=8))

    def test_module_imports_do_not_connect_to_postgres(self):
        with patch("sqlalchemy.engine.Engine.connect") as connect:
            for name in ("rag.config", "rag.setup", "rag.vector_store", "rag.service"):
                importlib.reload(importlib.import_module(name))
        connect.assert_not_called()


class RagServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = RagSettings(
            _env_file=None, embedding_dimensions=8, chunk_size=40, chunk_overlap=5,
        )
        self.store = InMemoryVectorStore(DeterministicFakeEmbedding(size=8))
        self.service = RagService(self.store, self.config)

    async def test_chunking_preserves_metadata_and_uses_repeatable_uuid_ids(self):
        content = "Montage der Solaranlage. " * 8
        ids = await self.service.add_text(content, source="angebot.pdf", metadata={"kunde_id": 7})
        self.assertGreater(len(ids), 1)
        self.assertEqual(len(set(ids)), len(ids))
        self.assertTrue(all(UUID(value).version == 5 for value in ids))
        chunks = await self.store.aget_by_ids(ids)
        self.assertEqual([chunk.metadata["chunk_index"] for chunk in chunks], list(range(len(ids))))
        self.assertTrue(all(chunk.metadata["source"] == "angebot.pdf" for chunk in chunks))
        self.assertTrue(all(chunk.metadata["kunde_id"] == 7 for chunk in chunks))
        repeated = await self.service.add_text(content, source="angebot.pdf", metadata={"kunde_id": 7})
        self.assertEqual(ids, repeated)
        other_source = await self.service.add_text(content, source="rechnung.pdf")
        self.assertTrue(set(ids).isdisjoint(other_source))

    async def test_search_retriever_and_deletion(self):
        ids = await self.service.add_text("Montage", source="angebot.pdf")
        matches = await self.service.search("Montage", k=1)
        self.assertEqual(matches[0].page_content, "Montage")
        self.assertEqual((await self.service.as_retriever(k=1).ainvoke("Montage"))[0].id, ids[0])
        await self.service.delete_chunks(ids)
        self.assertEqual(await self.service.search("Montage"), [])
        self.assertFalse(await self.service.delete_chunks([]))

    async def test_metadata_filters_are_forwarded_to_the_vector_store(self):
        filters = {"kunde_id": {"$eq": 7}}
        with patch.object(self.store, "asimilarity_search", new_callable=AsyncMock) as search:
            search.return_value = []
            await self.service.search("Montage", k=2, filters=filters)
        search.assert_awaited_once_with("Montage", k=2, filter=filters)

    async def test_empty_inputs_and_nonpositive_result_limits_are_rejected(self):
        for content, source in ((" ", "document.pdf"), ("Text", " ")):
            with self.assertRaises(ValueError):
                await self.service.add_text(content, source=source)
        with self.assertRaises(ValueError):
            await self.service.search(" ")
        with self.assertRaises(ValueError):
            self.service.as_retriever(k=0)

    async def test_vector_store_closes_pool_after_success_and_failure(self):
        embeddings = DeterministicFakeEmbedding(size=8)
        for fail in (False, True):
            with (
                self.subTest(fail=fail),
                patch("rag.vector_store.PGEngine") as pg_engine,
                patch("rag.vector_store.create_async_engine"),
                patch("rag.vector_store.PGVectorStore.create", new_callable=AsyncMock) as create,
            ):
                engine = pg_engine.from_engine.return_value
                engine.close = AsyncMock()
                if fail:
                    create.side_effect = RuntimeError("missing table")
                    with self.assertRaisesRegex(RuntimeError, "missing table"):
                        async with open_vector_store(embeddings, "postgresql+psycopg://test", self.config):
                            self.fail("The failing store must not be returned")
                else:
                    async with open_vector_store(embeddings, "postgresql+psycopg://test", self.config) as store:
                        self.assertIs(store, create.return_value)
                engine.close.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
