import logging
from pathlib import Path

from app.ingestion.loader import load_documents
from app.ingestion.cleaner import clean_documents
from app.ingestion.chunker import split_documents
from app.ingestion.metadata import enrich_metadata
from app.ingestion.storage import save_chunks
from app.retrieval.embeddings import get_embeddings
from app.retrieval.vector_store import recreate_vector_store

logger = logging.getLogger(__name__)


def run_ingestion(data_dir: str | Path | None = None) -> int:
    logger.info("Starting ingestion pipeline")

    raw_docs = load_documents(data_dir)
    logger.info("Loaded %s raw documents", len(raw_docs))

    cleaned_docs = clean_documents(raw_docs)
    logger.info("Cleaned documents count: %s", len(cleaned_docs))

    chunks = split_documents(cleaned_docs)
    logger.info("Split into %s chunks", len(chunks))

    enriched_chunks = enrich_metadata(chunks)

    if enriched_chunks:
        sample = enriched_chunks[0]
        logger.info("Sample chunk metadata: %s", sample.metadata)

    save_chunks(enriched_chunks)
    logger.info("Saved processed chunks to %s", data_dir if data_dir else "processed store")

    embeddings = get_embeddings()
    recreate_vector_store(enriched_chunks, embeddings)

    logger.info("Ingestion completed successfully")

    return len(enriched_chunks)