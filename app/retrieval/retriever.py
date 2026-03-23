from app.retrieval.embeddings import get_embeddings
from app.retrieval.vector_store import load_vector_store


def get_retriever(k: int = 5):
    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings)
    return vector_store.as_retriever(search_kwargs={"k": k})