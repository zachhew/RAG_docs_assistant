from langchain_openai import ChatOpenAI

from app.core.config import settings


def get_llm() -> ChatOpenAI:
    if not settings.llm_api_key:
        raise ValueError("LLM_API_KEY is not set. Please provide it in the .env file.")
    return ChatOpenAI(
        model=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.1,
        max_tokens=settings.llm_max_tokens,
    )