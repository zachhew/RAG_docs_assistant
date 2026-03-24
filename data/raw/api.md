# API Layer

The API layer exposes endpoints for interacting with the RAG assistant.

## Main Endpoint

The main endpoint is responsible for receiving a user question and returning an answer.

## Request Schema

The request contains:

- question
- top_k

## Response Schema

The response contains:

- answer
- citations

## Citations

Citations help users understand which document chunks were used to build the answer.

## Validation

The API should validate that:

- the question is not empty
- top_k is within a reasonable range