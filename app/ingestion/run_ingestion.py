from app.core.logging import setup_logging
from app.ingestion.pipeline import run_ingestion


if __name__ == "__main__":
    setup_logging()
    total_chunks = run_ingestion()
    print(f"Indexed chunks: {total_chunks}")