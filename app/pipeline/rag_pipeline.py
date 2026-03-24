import json
import logging

from app.core.config import settings
from app.llm.client import get_llm
from app.pipeline.prompt_builder import build_prompt
from app.pipeline.query_rewriter import rewrite_query, should_rewrite_query
from app.pipeline.response_builder import build_citations
from app.retrieval.hybrid import hybrid_retrieve_multi
from app.retrieval.reranker import rerank_documents
from app.retrieval.retriever import get_retriever

logger = logging.getLogger(__name__)


def _dense_retrieve(question: str, top_k: int):
    retriever = get_retriever(k=max(top_k, settings.retrieval_fetch_k))
    return retriever.invoke(question)


def _hybrid_retrieve(question: str, top_k: int):
    from app.retrieval.hybrid import hybrid_retrieve
    return hybrid_retrieve(question=question, top_k=top_k)


def _maybe_build_retrieval_queries(question: str, use_query_rewriting: bool) -> list[str]:
    retrieval_queries = [question]

    if use_query_rewriting and should_rewrite_query(question):
        rewritten_query = rewrite_query(question)
        if rewritten_query and rewritten_query != question:
            retrieval_queries.append(rewritten_query)
    else:
        logger.info("Skipping query rewriting for question=%r", question)

    return retrieval_queries


def _get_documents(
    question: str,
    top_k: int = 5,
    mode: str = "hybrid_rerank",
    use_query_rewriting: bool = False,
):
    retrieval_queries = _maybe_build_retrieval_queries(
        question=question,
        use_query_rewriting=use_query_rewriting,
    )

    logger.info("Pipeline mode=%s | retrieval_queries=%r", mode, retrieval_queries)

    if mode == "dense":
        documents = _dense_retrieve(question=question, top_k=top_k)

    elif mode == "dense_rerank":
        retrieved_documents = _dense_retrieve(question=question, top_k=top_k)

        logger.info("Dense retrieved %s documents", len(retrieved_documents))
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

    elif mode == "hybrid_rerank":
        if use_query_rewriting and len(retrieval_queries) > 1:
            retrieved_documents = hybrid_retrieve_multi(
                queries=retrieval_queries,
                top_k=top_k,
            )
        else:
            retrieved_documents = _hybrid_retrieve(question=question, top_k=top_k)

        logger.info(
            "Hybrid retrieved %s unique documents for queries=%r",
            len(retrieved_documents),
            retrieval_queries,
        )

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

    else:
        raise ValueError(f"Unsupported pipeline mode: {mode}")

    logger.info("After retrieval/rerank | kept=%s | mode=%s", len(documents), mode)

    for i, doc in enumerate(documents, start=1):
        preview = " ".join(doc.page_content[:120].split())
        logger.info(
            "Final docs | doc=%s | chunk_id=%s | source=%s | score=%s | preview=%s",
            i,
            doc.metadata.get("chunk_id"),
            doc.metadata.get("source"),
            doc.metadata.get("score"),
            preview,
        )

    return documents


def run_rag_pipeline(
    question: str,
    top_k: int = 5,
    mode: str = "hybrid_rerank",
    use_query_rewriting: bool = False,
):
    documents = _get_documents(
        question=question,
        top_k=top_k,
        mode=mode,
        use_query_rewriting=use_query_rewriting,
    )

    prompt = build_prompt(question, documents)

    llm = get_llm()
    response = llm.invoke(prompt)

    citations = build_citations(documents)

    return {
        "answer": response.content,
        "citations": citations,
    }


def stream_rag_pipeline(
    question: str,
    top_k: int = 5,
    mode: str = "hybrid_rerank",
    use_query_rewriting: bool = False,
):
    documents = _get_documents(
        question=question,
        top_k=top_k,
        mode=mode,
        use_query_rewriting=use_query_rewriting,
    )

    prompt = build_prompt(question, documents)
    citations = build_citations(documents)
    llm = get_llm()

    logger.info("Starting streaming response | mode=%s | question=%r", mode, question)

    def event_stream():
        full_answer_parts = []

        try:
            for chunk in llm.stream(prompt):
                text = chunk.content if chunk.content else ""
                if text:
                    full_answer_parts.append(text)
                    payload = {
                        "type": "token",
                        "content": text,
                    }
                    yield json.dumps(payload, ensure_ascii=False) + "\n"

            full_answer = "".join(full_answer_parts)

            logger.info(
                "Streaming completed | answer_length=%s | citations=%s",
                len(full_answer),
                len(citations),
            )

            final_payload = {
                "type": "final",
                "answer": full_answer,
                "citations": [citation.model_dump() for citation in citations],
            }
            yield json.dumps(final_payload, ensure_ascii=False) + "\n"

        except Exception:
            logger.exception("Streaming failed for question=%r", question)
            error_payload = {
                "type": "error",
                "message": "Streaming failed",
            }
            yield json.dumps(error_payload, ensure_ascii=False) + "\n"

    return event_stream()