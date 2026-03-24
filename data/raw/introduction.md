# Advanced RAG Assistant

Advanced RAG Assistant is a documentation question-answering system built with FastAPI, Qdrant, and LLMs.

## Purpose

The system helps users ask questions about technical documentation and receive grounded answers with citations.

## Core Features

- document ingestion
- text chunking
- vector search
- citation generation
- retrieval-augmented generation

## Architecture Overview

The project is divided into several modules:

- API layer for user requests
- ingestion pipeline for loading and chunking documents
- retrieval layer for vector search
- pipeline layer for RAG orchestration
- LLM layer for answer generation

## Notes

The assistant should answer only from the indexed documentation.
If the answer is missing in the context, it should say that it does not know.