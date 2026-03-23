from fastapi import FastAPI

from app.api.routes import ask
from app.core.logging import setup_logging

setup_logging()
app = FastAPI(
    title = "Advanced RAG support",
    description="Advanced RAG support",
    version="0.1.0",
)

app.include_router(ask.router)