import logging

from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


def should_rewrite_query(question: str) -> bool:
    stripped = question.strip()

    if not settings.enable_query_rewriting:
        return False

    if len(stripped.split()) < settings.query_rewriting_min_words:
        return True

    vague_patterns = [
        "how does it",
        "how does this",
        "what about",
        "how is it",
        "how does this thing",
        "what does it do",
    ]

    lowered = stripped.lower()
    return any(pattern in lowered for pattern in vague_patterns)


def get_query_rewriter_llm() -> ChatOpenAI:
    if not settings.llm_api_key:
        raise ValueError("LLM_API_KEY is not set. Please provide it in the .env file.")

    return ChatOpenAI(
        model=settings.query_rewriter_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.0,
    )


def rewrite_query(question: str) -> str:
    llm = get_query_rewriter_llm()

    prompt = f"""
You rewrite user questions for retrieval over a technical documentation corpus.

Rules:
- preserve the original meaning strictly
- do not answer the question
- do not generalize the query
- do not invent entities, processes, or features
- if the question is ambiguous, keep it close to the original wording
- prefer explicit technical wording only when strongly implied by the question
- return only one rewritten query
- return only plain text

User question:
{question}
""".strip()

    response = llm.invoke(prompt)
    rewritten = response.content.strip()

    if not rewritten:
        logger.warning("Query rewriting returned empty output, using original question")
        return question

    logger.info("Query rewritten | original=%r | rewritten=%r", question, rewritten)
    return rewritten

# What metadata does each chunk contain?
# What does the API response contain?
# What settings should be stored in configuration?
# What does Qdrant provide?