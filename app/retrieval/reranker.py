from sentence_transformers import CrossEncoder

from app.core.config import settings

_reranker = None


def get_reranker() -> CrossEncoder:
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(
            settings.reranker_model_name,
            device=settings.reranker_device,
        )

    return _reranker


def rerank_documents(
    question: str,
    documents: list,
    top_k: int = 5,
    min_score: float | None = None,
) -> list:
    if not documents:
        return []

    reranker = get_reranker()
    pairs = [(question, doc.page_content) for doc in documents]
    scores = reranker.predict(pairs, show_progress_bar=False)

    scored_docs = []
    for doc, score in zip(documents, scores):
        doc.metadata["score"] = float(score)
        scored_docs.append(doc)

    scored_docs.sort(
        key=lambda d: d.metadata.get("score", float("-inf")),
        reverse=True,
    )

    if min_score is None:
        return scored_docs[:top_k]

    filtered_docs = [
        doc for doc in scored_docs
        if doc.metadata.get("score", float("-inf")) >= min_score
    ]

    if filtered_docs:
        return filtered_docs[:top_k]

    fallback_k = min(2, len(scored_docs))
    return scored_docs[:fallback_k]