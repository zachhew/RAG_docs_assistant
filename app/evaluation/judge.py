import json
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from app.core.config import settings


class JudgeResult(BaseModel):
    answer_relevance: int = Field(..., ge=1, le=5)
    groundedness: int = Field(..., ge=1, le=5)
    completeness: int = Field(..., ge=1, le=5)
    hallucination_detected: bool
    comment: str


def get_judge_llm() -> ChatOpenAI:
    if not settings.llm_api_key:
        raise ValueError("LLM_API_KEY is not set. Please provide it in the .env file.")

    return ChatOpenAI(
        model=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.0,
    )


def judge_answer(question: str, answer: str, citations: list[dict]) -> JudgeResult:
    llm = get_judge_llm()

    citations_text = json.dumps(citations, ensure_ascii=False, indent=2)

    prompt = f"""
You are evaluating a RAG system answer.

Evaluate the answer using the following criteria:
1. answer_relevance: how well the answer addresses the question (1-5)
2. groundedness: how well the answer is supported by the provided citations/context (1-5)
3. completeness: how complete and useful the answer is (1-5)
4. hallucination_detected: true if the answer contains unsupported claims
5. comment: one short explanation

Rules:
- be strict
- use only the question, answer, and citations provided
- return valid JSON only
- do not include markdown fences

Question:
{question}

Answer:
{answer}

Citations:
{citations_text}
""".strip()

    response = llm.invoke(prompt)
    raw = response.content.strip()

    data = json.loads(raw)
    return JudgeResult(**data)