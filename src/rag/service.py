"""Chunk document text, store embeddings, and retrieve context for a later RAG chain."""

from typing import Any
from uuid import NAMESPACE_URL, uuid5
import json

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import RagSettings


class RagService:
    def __init__(self, vector_store: VectorStore, config: RagSettings | None = None):
        self.vector_store = vector_store
        self.config = config or RagSettings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            add_start_index=True,
        )

    async def add_text(
        self,
        text: str,
        *,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[str]:
        """Index Docling Markdown/text, preserving metadata and stable UUID chunk IDs.

        Unchanged chunks upsert under the same IDs. Retain returned IDs to delete
        obsolete chunks before replacing or removing an entire source document.
        """
        if not text.strip() or not source.strip():
            raise ValueError("text and source must not be empty")
        document = Document(page_content=text, metadata={**(metadata or {}), "source": source})
        chunks = self.splitter.split_documents([document])
        ids = []
        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index
            identity = json.dumps([source, index, chunk.page_content], ensure_ascii=False)
            chunk.id = str(uuid5(NAMESPACE_URL, identity))
            ids.append(chunk.id)
        return await self.vector_store.aadd_documents(chunks, ids=ids)

    def as_retriever(
        self, *, k: int | None = None, filters: dict[str, Any] | None = None,
    ) -> VectorStoreRetriever:
        """Return a retriever usable by LangChain chains via await retriever.ainvoke()."""
        limit = self.config.search_k if k is None else k
        if limit <= 0:
            raise ValueError("k must be positive")
        search_kwargs: dict[str, Any] = {"k": limit}
        if filters is not None:
            search_kwargs["filter"] = filters
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

    async def search(
        self, query: str, *, k: int | None = None, filters: dict[str, Any] | None = None,
    ) -> list[Document]:
        if not query.strip():
            raise ValueError("query must not be empty")
        return await self.as_retriever(k=k, filters=filters).ainvoke(query)

    async def delete_chunks(self, ids: list[str]) -> bool | None:
        """Delete only the supplied chunk UUIDs; never delete a whole collection."""
        if not ids:
            return False
        return await self.vector_store.adelete(ids=ids)
