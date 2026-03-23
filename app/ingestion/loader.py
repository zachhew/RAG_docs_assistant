from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

from app.core.config import settings


def _load_single_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()

    if suffix in {".md", ".txt"}:
        loader = TextLoader(str(path), encoding="utf-8")
        return loader.load()

    return []


def load_documents(data_dir: str | Path | None = None) -> list[Document]:
    base_dir = Path(data_dir) if data_dir else settings.raw_data_dir

    if not base_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {base_dir}")

    documents: list[Document] = []

    for path in sorted(base_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in settings.supported_extensions:
            continue

        documents.extend(_load_single_file(path))

    return documents