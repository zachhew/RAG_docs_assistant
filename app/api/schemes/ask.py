from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User question about the documentation")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of retrieved chunks to use")


class Citation(BaseModel):
    chunk_id: int = Field(..., description="Chunk identifier")
    source: str = Field(..., description="Document source path")
    title: str = Field(..., description="Document title")
    url: str | None = Field(default=None, description="Source URL if available")
    score: float | None = Field(default=None, description="Retrieval or reranker score")


class AskResponse(BaseModel):
    answer: str = Field(..., description="Generated grounded answer")
    citations: list[Citation] = Field(default_factory=list, description="Supporting citations")