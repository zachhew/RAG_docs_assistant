from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import settings


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
    )


def recreate_vector_store(documents, embeddings) -> QdrantVectorStore:
    client = get_qdrant_client()

    collections = client.get_collections().collections
    collection_names = {collection.name for collection in collections}

    if settings.collection_name in collection_names:
        client.delete_collection(settings.collection_name)

    return QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        url=settings.qdrant_url,
        collection_name=settings.collection_name,
        force_recreate=True,
    )


def load_vector_store(embeddings) -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=settings.qdrant_url,
        collection_name=settings.collection_name,
    )