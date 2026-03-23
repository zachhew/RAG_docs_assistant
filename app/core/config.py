from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "RAG Docs Assistant"

    raw_data_dir: Path = BASE_DIR / "data" / "raw"
    processed_chunks_path: Path = BASE_DIR / "data" / "processed" / "chunks.json"

    qdrant_url: str = "http://localhost:6333"
    collection_name: str = "docs_collection"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2" #временно
    embedding_device: str = "cpu"

    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_api_key: str | None = None
    llm_model_name: str = "openai/gpt-4o-mini"

    query_rewriter_model_name: str = "openai/gpt-4o-mini"
    enable_query_rewriting: bool = False
    query_rewriting_min_words: int = 5

    reranker_model_name: str = "BAAI/bge-reranker-base" #временно?
    reranker_device: str = "cpu"

    chunk_size: int = 700
    chunk_overlap: int = 120
    llm_max_tokens: int = 1000
    retrieval_fetch_k: int = 10
    bm25_fetch_k: int = 10
    reranker_min_score: float = 0.2

    supported_extensions: tuple[str, ...] = (".md", ".txt")


settings = Settings()