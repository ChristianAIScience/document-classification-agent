"""Configuration for the vector table, chunking, and retrieval."""

from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RagSettings(BaseSettings):
    table_name: str = Field(
        default="rag_document_chunks", max_length=63, pattern=r"^[a-z][a-z0-9_]*$",
    )
    embedding_dimensions: int = Field(default=768, gt=0)
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)
    search_k: int = Field(default=4, gt=0)

    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    @model_validator(mode="after")
    def validate_chunk_overlap(self) -> "RagSettings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self
