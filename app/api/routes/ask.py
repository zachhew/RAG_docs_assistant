from fastapi import APIRouter

from app.api.schemes.ask import AskRequest, AskResponse
from app.pipeline.rag_pipeline import run_rag_pipeline

router = APIRouter()
@router.post("/ask", response_model=AskResponse)
async def ask_docs(request: AskRequest):
    result = run_rag_pipeline(
        question=request.question,
        top_k=request.top_k,
    )

    return AskResponse(
        answer=result["answer"],
        citations=result["citations"],
    )