# EssaSearch - Integration Guide

This guide explains how to integrate the EssaSearch engine into your own applications using its RESTful API.

## API Base URL
When running locally or via Docker, the API is available at:
`http://localhost:8000`

FastAPI provides an automatic Swagger UI documentation page at:
`http://localhost:8000/docs`

## 1. Indexing a Document
Add a new document to the search index.

**Endpoint:** `POST /index`
**Content-Type:** `application/json`

### Payload
```json
{
  "id": "doc_123",
  "content": "The quick brown fox jumps over the lazy dog.",
  "metadata": {
    "author": "Alice",
    "category": "nature"
  }
}
```

### cURL Example
```bash
curl -X 'POST' \
  'http://localhost:8000/index' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "1",
  "content": "The fast brown fox leaps.",
  "metadata": {"author": "Test"}
}'
```

## 2. Searching Documents
Search the index using a natural language query. Results are ranked using the BM25 algorithm.

**Endpoint:** `POST /search`
**Content-Type:** `application/json`

### Payload
```json
{
  "query": "fast fox",
  "limit": 10
}
```

### Response
```json
{
  "status": "success",
  "query": "fast fox",
  "hits": 1,
  "results": [
    {
      "id": "1",
      "score": 1.2345,
      "content": "The fast brown fox leaps.",
      "metadata": {
        "author": "Test"
      }
    }
  ]
}
```

## 3. Getting Engine Stats
Retrieve current metrics of the search engine's internal data structures.

**Endpoint:** `GET /stats`

### Response
```json
{
  "total_documents": 1,
  "total_terms": 4
}
```

## Advanced Python Integration
If you wish to bypass the HTTP API and use the core engine directly within a Python application:

```python
from essasearch.engine import SearchEngine

engine = SearchEngine()

# Indexing
engine.index_document("doc1", "EssaSearch is highly optimized.", {"env": "prod"})

# Searching
results = engine.search("optimized search", limit=5)

for res in results:
    print(f"Match: {res['id']} with score {res['score']}")
```
