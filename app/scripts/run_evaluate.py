import json
from pathlib import Path

from app.core.logging import setup_logging
from app.evaluation.judge import judge_answer
from app.pipeline.rag_pipeline import run_rag_pipeline


BASE_DIR = Path(__file__).resolve().parent.parent.parent
EVAL_PATH = BASE_DIR / "data" / "eval" / "eval_questions.json"
# MODES = ["dense", "dense_rerank", "hybrid_rerank", "hybrid_rerank_rewrite"]
MODES = ["hybrid_rerank"]


def load_eval_questions():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    return text.lower().strip()


def contains_expected_keywords(answer: str, expected_keywords: list[str]) -> bool:
    answer_norm = normalize_text(answer)
    return all(keyword.lower() in answer_norm for keyword in expected_keywords)


def contains_expected_source(citations: list[dict], expected_sources: list[str]) -> bool:
    found_sources = {item["source"] for item in citations}
    return any(source in found_sources for source in expected_sources)


def evaluate_mode(mode: str, questions: list[dict], top_k: int = 5):
    results = []

    if mode == "hybrid_rerank_rewrite":
        pipeline_mode = "hybrid_rerank"
        use_query_rewriting = True
    else:
        pipeline_mode = mode
        use_query_rewriting = False

    for item in questions:
        result = run_rag_pipeline(
            question=item["question"],
            top_k=top_k,
            mode=pipeline_mode,
            use_query_rewriting=use_query_rewriting,
        )

        citations = [
            {
                "source": citation.source,
                "chunk_id": citation.chunk_id,
                "score": citation.score,
            }
            for citation in result["citations"]
        ]

        source_hit = contains_expected_source(citations, item["expected_sources"])
        keyword_hit = contains_expected_keywords(result["answer"], item["expected_keywords"])

        judge = judge_answer(
            question=item["question"],
            answer=result["answer"],
            citations=citations,
        )

        results.append(
            {
                "id": item["id"],
                "question": item["question"],
                "mode": mode,
                "answer": result["answer"],
                "citations": citations,
                "source_hit": source_hit,
                "keyword_hit": keyword_hit,
                "judge": judge.model_dump(),
            }
        )

    return results


def summarize(results: list[dict], mode: str):
    total = len(results)
    source_hits = sum(1 for r in results if r["source_hit"])
    keyword_hits = sum(1 for r in results if r["keyword_hit"])

    avg_relevance = sum(r["judge"]["answer_relevance"] for r in results) / total
    avg_groundedness = sum(r["judge"]["groundedness"] for r in results) / total
    avg_completeness = sum(r["judge"]["completeness"] for r in results) / total
    hallucination_count = sum(1 for r in results if r["judge"]["hallucination_detected"])

    print(f"\n=== Mode: {mode} ===")
    print(f"Total questions: {total}")
    print(f"Source hit rate: {source_hits}/{total}")
    print(f"Keyword hit rate: {keyword_hits}/{total}")
    print(f"Avg relevance: {avg_relevance:.2f}/5")
    print(f"Avg groundedness: {avg_groundedness:.2f}/5")
    print(f"Avg completeness: {avg_completeness:.2f}/5")
    print(f"Hallucinations flagged: {hallucination_count}/{total}")

    for r in results:
        print(f"\n[{r['id']}] {r['question']}")
        print(f"source_hit={r['source_hit']} | keyword_hit={r['keyword_hit']}")
        print("citations:", [c["source"] for c in r["citations"]])
        print("answer:", r["answer"])
        print("judge:", r["judge"])


def main():
    setup_logging()
    questions = load_eval_questions()

    for mode in MODES:
        results = evaluate_mode(mode, questions)
        summarize(results, mode)


if __name__ == "__main__":
    main()