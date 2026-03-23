from langchain_community.retrievers import BM25Retriever

from app.core.config import settings
from app.ingestion.storage import load_chunks

_bm25_retriever = None


def get_bm25_retriever():
    global _bm25_retriever

    if _bm25_retriever is None:
        documents = load_chunks()
        retriever = BM25Retriever.from_documents(documents)
        retriever.k = settings.bm25_fetch_k
        _bm25_retriever = retriever

    return _bm25_retriever