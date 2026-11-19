"""Explicit, repeatable setup of the pgvector extension and chunk table."""

from sqlalchemy import Engine, text

from rag.config import RagSettings


def initialize_vector_store(engine: Engine, config: RagSettings | None = None) -> None:
    """Create missing objects without dropping data or altering existing tables."""
    config = config or RagSettings()
    # The table name is restricted to a PostgreSQL identifier by RagSettings.
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.execute(text(f'''
            CREATE TABLE IF NOT EXISTS public."{config.table_name}" (
                langchain_id UUID PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({config.embedding_dimensions}) NOT NULL,
                source TEXT NOT NULL,
                dokument_id BIGINT,
                kunde_id BIGINT,
                dokumententyp TEXT,
                chunk_index INTEGER NOT NULL,
                langchain_metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb
            )
        '''))
        vector_type = connection.execute(text('''
            SELECT format_type(a.atttypid, a.atttypmod)
            FROM pg_attribute AS a
            JOIN pg_class AS c ON c.oid = a.attrelid
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relname = :table_name
                AND a.attname = 'embedding' AND NOT a.attisdropped
        '''), {"table_name": config.table_name}).scalar_one()
        if vector_type != f"vector({config.embedding_dimensions})":
            raise ValueError(
                f"Existing embedding column is {vector_type}; expected "
                f"vector({config.embedding_dimensions}). Use another table or migrate explicitly."
            )
