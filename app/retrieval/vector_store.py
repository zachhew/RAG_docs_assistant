from langchain_qdrant import QdrantVectorStore

from app.core.config import settings

_vector_store = None


def recreate_vector_store(documents, embeddings) -> QdrantVectorStore:
    return QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        url=settings.qdrant_url,
        collection_name=settings.collection_name,
        force_recreate=True,
    )


def load_vector_store(embeddings) -> QdrantVectorStore:
    global _vector_store

    if _vector_store is None:
        _vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            url=settings.qdrant_url,
            collection_name=settings.collection_name,
        )

    return _vector_store