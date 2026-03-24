# Configuration

The project uses centralized configuration to manage application settings.

## Why Configuration Matters

Configuration keeps important parameters in one place.
This makes the project easier to maintain, test, and deploy.

## Examples of Configuration Values

The system may store the following settings:

- raw data directory
- Qdrant URL
- collection name
- embedding model name
- embedding device
- chunk size
- chunk overlap
- supported file extensions
- LLM model name
- LLM API key
- LLM base URL

## Environment Variables

Sensitive values such as API keys should not be hardcoded.
They should be loaded from environment variables or a .env file.

## Benefits of Centralized Config

Centralized configuration helps with:

- local development
- Docker deployment
- model switching
- reproducibility
- cleaner code organization

## Example Use Cases

A developer may change the chunk size to test retrieval quality.
A different embedding model may be selected for experimentation.
The LLM provider can be changed without rewriting business logic.