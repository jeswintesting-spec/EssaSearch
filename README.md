# EssaSearch
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Docker](https://img.shields.io/badge/Docker-Supported-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A high-performance, full-text distributed search engine written entirely in Python. EssaSearch demonstrates an understanding of advanced data structures and search algorithms utilized by industry leaders like Google and Amazon.

## 🚀 Key Features
- **Docker Containerization:** Fully containerized architecture using `docker-compose` for instant, OS-agnostic deployments of the entire cluster.
- **Python Client SDK:** Includes a clean, object-oriented `EssaClient` SDK allowing developers to seamlessly integrate the search engine into their own Python applications.
- **Sleek Web Frontend:** A beautiful, responsive single-page web UI built with HTML/CSS/JS that interacts directly with the backend API to provide real-time search results, latency metrics, and highlighted snippets.
- **Cluster Backup & Restore:** Point-in-time snapshotting allows you to compress the entire search engine (memory and immutable disk segments) into a single `.zip` archive, and instantly restore the cluster from a backup.
- **LRU Query Caching:** Employs a custom Least Recently Used (LRU) Cache to store frequent search queries, eliminating redundant AST evaluations and vector math to guarantee `O(1)` ultra-low latency response times.
- **Contextual Snippet Highlighting:** Dynamically scans documents to generate Google-style search snippets, centering the preview around the highest density of query terms and injecting rich terminal highlighting.
- **Hybrid Search (Semantic + Keyword):** Combines dense vector embeddings (via `sentence-transformers`) using cosine similarity with sparse BM25 ranking to deliver the most semantically relevant search results.
- **AST Query Parser:** A custom Recursive Descent Parser that builds an Abstract Syntax Tree (AST) to support advanced boolean queries like `author:Alice AND (fox OR dog) NOT lazy`.
- **Thread-Safe Concurrency (Read-Write Locks):** A custom-built synchronization primitive using `threading.Condition` ensures thousands of simultaneous search queries (reads) can execute concurrently, while safely isolating index mutations (writes) to prevent data corruption or writer starvation.
- **Disk Persistence & Segment Merging (LSM-Tree style):** Automatically flushes in-memory indexes to immutable disk segments, with a background merge process to optimize query speed and eliminate fragmentation.
- **Typo Tolerance & Fuzzy Search:** Implements a custom **Prefix Tree (Trie)** and dynamic programming **Levenshtein Distance** algorithm to correct typos and find closest matches on the fly.
- **Inverted Index Engine:** A custom, highly-optimized data structure mapping tokenized words to document IDs.
- **BM25 / TF-IDF Ranking Algorithm:** Complex algorithmic relevance scoring to ensure the most accurate search results, rather than just returning exact keyword matches.
- **REST API Server:** Built on FastAPI to enable easy distributed node deployments.
- **Rich CLI Client:** A beautifully formatted, interactive terminal interface for managing the search engine.

## 🛠 Quick Start

### 1. Running Locally (Python)
```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic rich requests pytest

# Start the search engine server
python main.py
```

### 2. Running the Interactive CLI
In a new terminal window:
```bash
python cli.py
```

### 3. Running with Docker
```bash
docker-compose up --build -d
```

## 📖 Documentation
- [User Manual](USER_MANUAL.md): Comprehensive guide on using the CLI and search engine concepts.
- [Integration Guide](INTEGRATION_GUIDE.md): Developer guide for integrating the Search API into your applications.
