"""Explicit RAG setup: uv run --extra rag python src/init_rag.py."""

import logging

from db.database import engine
from rag.setup import initialize_vector_store


def main() -> None:
    try:
        initialize_vector_store(engine)
        logging.info("RAG vector table initialized.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
    main()
