# Vector Store

The vector store is responsible for storing document embeddings and retrieving relevant chunks.

## Purpose

After documents are cleaned and split into chunks, each chunk is converted into an embedding vector.
These vectors are stored in the vector database.

## Current Backend

The project uses Qdrant as the vector store backend.

## Why Qdrant

Qdrant provides:

- persistent storage
- vector similarity search
- metadata support
- collection management
- compatibility with modern retrieval pipelines

## Stored Data

Each indexed chunk contains:

- vector embedding
- page content
- metadata

## Metadata Examples

Metadata may include:

- chunk_id
- source
- title
- url

## Retrieval

At query time, the vector store receives an embedded user question and returns the most similar chunks.

## Future Improvements

The vector store can later be combined with:

- hybrid retrieval
- metadata filtering
- reranking