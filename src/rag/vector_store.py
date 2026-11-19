"""LangChain PostgreSQL vector-store lifecycle with no import-time connections."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langchain_core.embeddings import Embeddings
from langchain_postgres import PGEngine, PGVectorStore
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import create_async_engine

from rag.config import RagSettings


@asynccontextmanager
async def open_vector_store(
    embeddings: Embeddings,
    connection: str | URL,
    config: RagSettings | None = None,
) -> AsyncIterator[PGVectorStore]:
    """Connect to an initialized table and always dispose of its connection pool.

    Embeddings must use the configured dimensions and the same model for both
    indexing and querying. The asyncpg pool uses the caller's event loop, including
    on Windows. This function never creates the extension or table.
    """
    config = config or RagSettings()
    url = make_url(connection)
    if url.get_backend_name() != "postgresql":
        raise ValueError("The vector store requires a PostgreSQL connection URL")
    pool = create_async_engine(url.set(drivername="postgresql+asyncpg"), pool_pre_ping=True)
    engine = PGEngine.from_engine(pool)
    try:
        store = await PGVectorStore.create(
            engine=engine,
            embedding_service=embeddings,
            table_name=config.table_name,
            schema_name="public",
            metadata_columns=["source", "dokument_id", "kunde_id", "dokumententyp", "chunk_index"],
            k=config.search_k,
        )
        yield store
    finally:
        await engine.close()
