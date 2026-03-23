from app.core.config import settings
from app.retrieval.bm25_retriever import get_bm25_retriever
from app.retrieval.retriever import get_retriever


def _doc_key(doc) -> tuple:
    return (
        doc.metadata.get("chunk_id"),
        doc.metadata.get("source"),
    )


def hybrid_retrieve(question: str, top_k: int):
    dense_k = max(top_k, settings.retrieval_fetch_k)
    bm25_k = max(top_k, settings.bm25_fetch_k)

    dense_retriever = get_retriever(k=dense_k)
    bm25_retriever = get_bm25_retriever()

    bm25_retriever.k = bm25_k

    dense_docs = dense_retriever.invoke(question)
    bm25_docs = bm25_retriever.invoke(question)

    merged = {}
    for doc in dense_docs + bm25_docs:
        merged[_doc_key(doc)] = doc

    return list(merged.values())