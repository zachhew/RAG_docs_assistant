# Ingestion Pipeline

The ingestion pipeline is responsible for preparing raw documentation files for retrieval.

## Steps

1. Load raw files from the data directory
2. Clean the text
3. Split documents into chunks
4. Enrich chunks with metadata
5. Store embeddings in the vector database

## Supported Formats

The initial version supports the following file types:

- markdown files
- text files

## Metadata

Each chunk should contain metadata fields:

- chunk_id
- source
- title
- url

## Why Ingestion Matters

Good ingestion improves retrieval quality.
If chunks are too large, retrieval may become noisy.
If chunks are too small, important context may be lost.