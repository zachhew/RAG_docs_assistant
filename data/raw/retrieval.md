# Retrieval System

The retrieval system finds the most relevant chunks for a user question.

## Baseline Retrieval

The baseline system uses vector search over embedded chunks.

## Future Improvements

The retrieval system can later be improved with:

- hybrid search
- reranking
- query rewriting
- metadata filtering

## Vector Search

Vector search compares the user query embedding with document chunk embeddings.

## Reranking

Reranking is used after retrieval.
The system first retrieves more chunks, then reranks them, and finally sends the best chunks to the language model.

## Goal

The goal of retrieval is not only to find similar text, but to provide the most useful evidence for answer generation.