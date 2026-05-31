# EssaSearch - User Manual

Welcome to the EssaSearch User Manual. EssaSearch is a high-performance full-text search engine designed to demonstrate complex data structures and ranking algorithms.

## 1. Core Concepts
- **Documents:** The fundamental unit of data in EssaSearch. Each document has a unique ID, textual content, and optional metadata (like author, date).
- **Analyzer Pipeline:** When a document is indexed, its text passes through an analyzer which:
  - **Tokenizes:** Splits text into lowercase alphanumeric words.
  - **Filters Stop-Words:** Removes common English words (e.g., "the", "is", "at") that don't add semantic value.
  - **Stems:** Reduces words to their root forms (e.g., "running" becomes "run", "foxes" becomes "fox").
- **Inverted Index:** Instead of scanning every document for a word, the engine maintains an index mapping every unique term directly to the documents that contain it. This makes querying incredibly fast.
- **BM25 Ranking:** Search results aren't just exact matches. BM25 scores relevance based on term frequency (how often a term appears in the document) and inverse document frequency (how rare the term is across the entire dataset).

## 2. Using the Interactive CLI
EssaSearch provides a beautiful terminal interface built with the `rich` library.

### Starting the CLI
Ensure the EssaSearch server is running (`python main.py`), then start the CLI:
```bash
python cli.py
```

### Main Menu Options
1. **Search Documents:** Enter a search query. The engine will analyze your query and return ranked results based on the BM25 algorithm. It handles stemming automatically (searching for "run" will match documents containing "running").
2. **Index New Document:** Add a new document to the engine. You will be prompted for an ID, the main text content, and an optional Author metadata field.
3. **View Engine Stats:** See real-time metrics, including the total number of documents indexed and the total number of unique terms residing in the inverted index.
4. **Exit:** Safely exit the client.

## 3. Best Practices
- **Descriptive IDs:** Use UUIDs or clear semantic IDs for your documents to prevent overwriting.
- **Rich Queries:** Because of the advanced analyzer, you can type natural language queries. The engine will intelligently filter and rank the results.
