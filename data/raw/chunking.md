# Chunking Strategy

Chunking is the process of splitting source documents into smaller text fragments before indexing.

## Why Chunking Matters

Chunking affects retrieval quality.
If chunks are too large, retrieval may include too much irrelevant context.
If chunks are too small, important information may be separated and lost.

## Current Strategy

The current system uses recursive character-based splitting.

### Parameters

- chunk_size
- chunk_overlap
- separators

## Overlap

Chunk overlap helps preserve continuity between neighboring chunks.
This is useful when one idea spans across multiple paragraphs.

## Recommended Practice

For technical documentation, chunking should try to keep headings and related paragraphs together.
A chunk should contain enough context to answer a question, but not so much that it becomes noisy.

## Risks

Poor chunking can reduce answer quality even if the embedding model is strong.
Chunking should be treated as a core retrieval decision, not just a preprocessing step.