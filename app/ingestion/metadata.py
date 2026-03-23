from pathlib import Path
from langchain_core.documents import Document


def enrich_metadata(documents: list[Document]) -> list[Document]:
    enriched = []

    for idx, doc in enumerate(documents):
        metadata = dict(doc.metadata)

        raw_source = metadata.get("source", "unknown")
        source_path = Path(raw_source)

        metadata["chunk_id"] = idx
        metadata["source"] = source_path.name if raw_source != "unknown" else "unknown"
        metadata["title"] = source_path.stem if raw_source != "unknown" else "unknown"
        metadata["url"] = metadata.get("url", None)

        enriched.append(
            Document(
                page_content=doc.page_content,
                metadata=metadata,
            )
        )

    return enriched