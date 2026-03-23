import logging

from app.core.config import settings
from app.llm.client import get_llm
from app.pipeline.prompt_builder import build_prompt
from app.pipeline.response_builder import build_citations
from app.retrieval.reranker import rerank_documents
from app.retrieval.retriever import get_retriever

logger = logging.getLogger(__name__)


def run_rag_pipeline(question: str, top_k: int = 5):
    fetch_k = max(top_k, settings.retrieval_fetch_k)

    retriever = get_retriever(k=fetch_k)
    retrieved_documents = retriever.invoke(question)

    logger.info("Retrieved %s documents for question=%r", len(retrieved_documents), question)

    for i, doc in enumerate(retrieved_documents, start=1):
        preview = " ".join(doc.page_content[:120].split())
        logger.info(
            "Before rerank | doc=%s | chunk_id=%s | source=%s | preview=%s",
            i,
            doc.metadata.get("chunk_id"),
            doc.metadata.get("source"),
            preview,
        )

    documents = rerank_documents(
        question=question,
        documents=retrieved_documents,
        top_k=top_k,
        min_score=settings.reranker_min_score,
    )

    logger.info(
        "After rerank and score filtering | kept=%s | min_score=%.3f",
        len(documents),
        settings.reranker_min_score,
    )

    for i, doc in enumerate(documents, start=1):
        preview = " ".join(doc.page_content[:120].split())
        logger.info(
            "After rerank | doc=%s | chunk_id=%s | source=%s | score=%.4f | preview=%s",
            i,
            doc.metadata.get("chunk_id"),
            doc.metadata.get("source"),
            doc.metadata.get("score", 0.0),
            preview,
        )

    prompt = build_prompt(question, documents)

    llm = get_llm()
    response = llm.invoke(prompt)

    citations = build_citations(documents)

    return {
        "answer": response.content,
        "citations": citations,
    }