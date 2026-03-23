import json

from langchain_core.documents import Document

from app.core.config import settings


def save_chunks(documents: list[Document]) -> None:
    settings.processed_chunks_path.parent.mkdir(parents=True, exist_ok=True)

    payload = []
    for doc in documents:
        payload.append(
            {
                "page_content": doc.page_content,
                "metadata": doc.metadata,
            }
        )

    with open(settings.processed_chunks_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_chunks() -> list[Document]:
    if not settings.processed_chunks_path.exists():
        raise FileNotFoundError(
            f"Processed chunks file not found: {settings.processed_chunks_path}"
        )

    with open(settings.processed_chunks_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        Document(
            page_content=item["page_content"],
            metadata=item["metadata"],
        )
        for item in data
    ]