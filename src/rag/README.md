# PostgreSQL RAG storage

This package stores document chunks and embeddings in PostgreSQL using pgvector
and LangChain's `PGVectorStore`. It provides the retrieval component for a later
RAG answer-generation chain. It uses the application's PostgreSQL database and a
separate `public.rag_document_chunks` table.
Vector connections use `asyncpg` on the caller's event loop, including on Windows;
the application's existing synchronous database connections keep using psycopg.

## Setup

```powershell
uv sync --extra rag
uv run python src/init_db.py
uv run --extra rag python src/init_rag.py
```

PostgreSQL must have pgvector installed on the server. The initialization user
needs permission to enable the `vector` extension and create the chunk table.
Initialization is repeatable and does not overwrite existing data. Imports and
normal vector-store connections never create database objects.

Optional settings in the root `.env`:

```dotenv
RAG_TABLE_NAME=rag_document_chunks
RAG_EMBEDDING_DIMENSIONS=768
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=150
RAG_SEARCH_K=4
```

Configure dimensions to match the supplied embedding model before initialization.
Use the same model for ingestion and search. Switching models requires a separate
table or an explicit rebuild, even when dimensions match. Setup rejects an existing
embedding column with different dimensions. Search initially uses exact cosine
distance; add a pgvector index when the data volume justifies it.

## Ingest and retrieve

Supply any configured LangChain `Embeddings` implementation; this module does not
choose a model provider or send embedding requests until ingestion or retrieval.
Call the async functions from an async application or with `asyncio.run()`.

```python
from langchain_core.embeddings import Embeddings

from db.database import engine
from rag.config import RagSettings
from rag.service import RagService
from rag.vector_store import open_vector_store


async def index_and_search(embeddings: Embeddings, markdown: str):
    config = RagSettings()
    async with open_vector_store(embeddings, engine.url, config) as store:
        rag = RagService(store, config)
        chunk_ids = await rag.add_text(
            markdown,
            source="uploads/angebot.pdf",
            metadata={"dokument_id": 12, "kunde_id": 3, "dokumententyp": "angebot"},
        )
        documents = await rag.search(
            "Welche Montageleistungen werden angeboten?",
            filters={"kunde_id": {"$eq": 3}},
        )
        # Also usable in a LangChain chain: await retriever.ainvoke(question).
        retriever = rag.as_retriever(k=4, filters={"dokumententyp": "angebot"})
        return chunk_ids, documents
```

`source`, `dokument_id`, `kunde_id`, `dokumententyp`, and `chunk_index` are dedicated
metadata columns supporting LangChain PostgreSQL filters. Other metadata is kept
in JSONB. These IDs are references, not foreign keys: document deletion through
the existing API does not yet delete vector chunks. Filtering is a retrieval
feature; callers must enforce access permissions separately.

Chunk UUIDs are stable for identical source/text/chunk positions, making repeated
ingestion upsert the same chunks. Keep returned IDs and call
`await rag.delete_chunks(chunk_ids)` when removing or replacing source content;
changed content is not an automatic full-source replacement. A batch of chunk
writes is not atomic. The context manager closes its pool after success or failure.

## Validation

```powershell
uv run --extra rag python tests/test_rag.py -v
```

Offline checks use deterministic fake embeddings and mocked PostgreSQL boundaries.
For an actual pgvector round trip, point the opt-in test at a dedicated test database:

```powershell
$env:TEST_RAG_DATABASE_URL = 'postgresql+psycopg://user:password@localhost:5432/rag_test'
uv run --extra rag python tests/test_rag_postgres.py -v
```

The integration test creates a uniquely named test table and drops only that table
afterward. It uses fake embeddings and makes no external model calls.

Integration API: [LangChain PostgreSQL documentation](https://github.com/langchain-ai/langchain-postgres).
