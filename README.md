# Advanced RAG Docs Assistant

Advanced RAG Docs Assistant — это модульная Retrieval-Augmented Generation система для ответов на вопросы по технической документации.

Проект создавался как исследовательская и инженерная RAG-система с:

- модульным ingestion-пайплайном
- dense retrieval
- BM25 retrieval
- hybrid retrieval
- reranking
- фильтрацией по score
- grounded-ответами с citations
- offline evaluation
- LLM-as-a-judge evaluation
- потоковыми ответами (streaming)

---

## 1. Цель проекта

Цель проекта — спроектировать и реализовать более сильный RAG-пайплайн для поиска и ответа по технической документации.

---

## 2. Основные возможности

### Retrieval pipeline
- Dense retrieval через embeddings + Qdrant
- BM25 lexical retrieval
- Hybrid retrieval через объединение dense и BM25 кандидатов
- Cross-encoder reranking
- Фильтрация кандидатов по score

### Генерация ответа
- Grounded answering только на основе найденного контекста
- Source-aware citations в API-ответе
- Настраиваемый `top_k`
- LLM backend через OpenRouter

### Инженерные возможности
- Отдельный ingestion pipeline
- Dockerized Qdrant
- Streaming endpoint
- Offline evaluation scripts
- LLM judge для оценки ответов

---

## 3. Пайплайны

### High-level pipeline

```text
raw docs
-> ingestion
-> chunks + metadata
-> Qdrant + processed chunk store

user question
-> retrieval
   -> dense
   -> BM25
   -> hybrid merge
-> reranker
-> score filtering
-> prompt builder
-> LLM
-> answer + citations
```
### Потоковый pipeline
```
user question
-> retrieval
   -> dense
   -> BM25
   -> hybrid merge
-> reranker
-> score filtering
-> prompt builder
-> LLM stream
-> token chunks
-> final answer + citations
```

## 4. Архитектура
```
app/
  api/
    routes/
    schemes/
  core/
    config.py
    logging.py
  evaluation/
    judge.py
  ingestion/
    chunker.py
    cleaner.py
    loader.py
    metadata.py
    pipeline.py
    storage.py
  llm/
    client.py
  pipeline/
    prompt_builder.py
    query_rewriter.py
    rag_pipeline.py
    response_builder.py
  retrieval/
    bm25_retriever.py
    embeddings.py
    hybrid.py
    reranker.py
    retriever.py
    vector_store.py
  scripts/
    run_evaluate.py
    run_ingestion.py
```

---

## 5. Компоненты системы

### 5.1 Ingestion

Ingestion pipeline отделён от runtime inference.

Он выполняет:
- загрузку документов
- очистку текста
- chunking
- обогащение metadata
- сохранение processed chunks
- индексацию в Qdrant

Каждый chunk получает metadata:
- chunk_id
- source
- title
- url

### 5.2 Dense retrieval

Dense retrieval использует embeddings и Qdrant для поиска семантически близких chunks.

Это baseline retrieval layer.

### 5.3 BM25 retrieval

BM25 используется как lexical / keyword-based retrieval layer.


### 5.4 Hybrid retrieval

Hybrid retrieval объединяет:
- dense retrieval candidates
- BM25 retrieval candidates

Далее объединённый набор кандидатов передаётся в reranker.

### 5.5 Reranker

Cross-encoder reranker используется для улучшения final ranking найденных chunks.

Это помогает поднять наиболее полезные evidence chunks наверх и уменьшить количество шумного контекста перед генерацией ответа.

### 5.6 Score filtering

Reranker scores используются для фильтрации слабых кандидатов.

Это позволило уменьшить шумные citations и улучшить итоговый evidence set.

### 5.7 Query rewriting

Query rewriting реализован как optional retrieval enhancement.

Однако начальные эксперименты на текущем корпусе показали, что:
- он не даёт стабильного прироста качества
- на неоднозначных вопросах иногда слишком обобщает query
- добавляет дополнительный LLM call и усложняет pipeline

Решение: query rewriting реализован, но выключен по умолчанию.

Это осознанное инженерное решение.

### 5.8 Evaluation

В проекте используются два слоя evaluation:

Rule-based evaluation
- expected source hit
- expected keyword hit

LLM-as-a-judge evaluation
- answer relevance
- groundedness
- completeness
- hallucination flag

### 5.9 Streaming

Streaming endpoint возвращает ответ постепенно, а затем отправляет final event с:
- полным answer
- citations

Это улучшает UX API и демонстрирует поддержку потоковой генерации в serving-слое.

---

##  6. Retrieval modes

Система поддерживает несколько режимов пайплайна для экспериментов и оценки:
- dense
- dense_rerank
- hybrid_rerank

Это позволяет напрямую сравнивать:
- dense retrieval baseline
- dense retrieval + reranking
- hybrid retrieval + reranking

---

## 7. Методология оценки

### 7.1 Rule-based evaluation

Был собран небольшой evaluation dataset, содержащий:
- question
- expected source(s)
- expected keywords

Это позволило оценивать:
- находит ли система нужный источник
- содержит ли ответ ожидаемую информацию

### 7.2 LLM judge

Дополнительная LLM использовалась как judge для оценки:
- relevance
- groundedness
- completeness
- hallucination detection

---

## 8. Пример метрик

#### Rule-based evaluation на текущем датасете

Для hybrid_rerank на текущем evaluation set были получены:
- Source hit rate: 6/6
- Keyword hit rate: 5/6

#### Пример LLM judge метрик для hybrid_rerank

Один из representative runs дал:
- Average relevance: 4.67 / 5
- Average groundedness: 4.17 / 5
- Average completeness: 4.17 / 5
- Hallucinations flagged: 0 / 6

#### Важное замечание про judge variability

Оценки LLM judge полезны, но не абсолютно стабильны между запусками.
Поэтому rule-based metrics использовались как основной стабильный сигнал.

---

##  9. Главные выводы

### 9.1 Dense retrieval baseline уже оказался сильным

На текущем корпусе dense retrieval сам по себе хорошо работает на простых factual questions.

### 9.2 Reranking всё равно оказался полезным

Даже когда rule-based metrics не улучшаются драматически, reranking заметно улучшает:
- evidence cleanliness
- citation precision
- final context quality

Это хорошо видно на retrieved candidate sets и финальных citations.

### 9.3 Hybrid retrieval архитектурно силён, но чувствителен к датасету

Hybrid retrieval остаётся самой сильной retrieval-архитектурой в проекте, но текущий корпус слишком маленький и чистый, чтобы его преимущество полностью проявилось количественно.

### 9.4 Query rewriting нельзя включать “вслепую”

Query rewriting легко реализовать, но не всегда разумно держать его включённым.

В этом проекте он был реализован, протестирован и затем отключён по умолчанию, потому что прирост качества оказался нестабильным на текущем корпусе.

Это один из главных практических выводов проекта.

### 9.5 Evaluation должна быть многослойной

Одной метрики недостаточно.

Наиболее полезной оказалась комбинация:
- source hit
- keyword hit
- LLM judge
- ручной просмотр citations и context cleanliness

---

## 10. API

### POST /ask

Возвращает обычный JSON-ответ:
```
{
  "answer": "The API response contains an answer and citations.",
  "citations": [
    {
      "chunk_id": 0,
      "source": "api.md",
      "title": "api",
      "url": null,
      "score": 0.91
    }
  ]
}
```
### POST /ask/stream

Возвращает потоковый ответ в формате NDJSON:
```
{"type":"token","content":"The "}
{"type":"token","content":"API "}
{"type":"token","content":"response "}
{"type":"final","answer":"The API response contains an answer and citations.","citations":[...]}
```

---
## 11. Конфигурация

Пример .env:
```
LLM_API_KEY=
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL_NAME=openai/gpt-4o-mini
QUERY_REWRITER_MODEL_NAME=openai/gpt-4o-mini
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL_NAME=BAAI/bge-reranker-base
```

Основные runtime-настройки хранятся в app/core/config.py, включая:
- embedding model
- reranker model
- qdrant url
- chunk size
- retrieval parameters
- score thresholds
- query rewriting flag
---

## 12. Как запустить проект

12.1 Запустить Qdrant
```
docker compose up -d
```
12.2 Прогнать ingestion
```
python -m app.scripts.run_ingestion
```
12.3 Запустить API
```
uvicorn app.main:app --reload
```
12.4 Прогнать evaluation
```
python -m app.scripts.run_evaluate
```
---
## 13.  Стек технологий
- Python
- FastAPI
- Qdrant
- LangChain
- OpenRouter
- Sentence Transformers
- BM25
- Cross-encoder reranking
