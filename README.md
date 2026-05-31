# 🔍 EssaSearch

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

A high-performance, distributed full-text and semantic search engine built entirely from scratch in Python. 

EssaSearch bridges the gap between classic keyword retrieval (Elasticsearch/Lucene) and modern AI vector databases. It leverages an Abstract Syntax Tree (AST) for complex boolean queries, an LSM-Tree for immutable disk persistence, and Sentence-Transformers for semantic understanding.

---

## 🚀 Key Architectural Features

### 🧠 Search & Retrieval
- **Hybrid Search Engine:** Fuses sparse **BM25/TF-IDF** keyword scoring with dense **Cosine Similarity** vector matching (via `sentence-transformers` & PyTorch) for unparalleled relevance.
- **AST Query Parser:** A custom Recursive Descent Parser compiler frontend that translates complex user queries (`author:Alice AND (fox OR dog) NOT lazy`) into an executable Abstract Syntax Tree.
- **Contextual Snippet Highlighting:** Dynamically scans documents and generates Google-style previews, centering around the highest density of query terms with rich formatting.
- **Typo Tolerance:** Implements a custom **Trie (Prefix Tree)** and dynamic programming **Levenshtein Distance** algorithms to correct typos instantly.

### ⚙️ Systems Engineering
- **Read-Write Lock Concurrency:** A custom synchronization primitive built on `threading.Condition` ensures thousands of simultaneous concurrent reads without starving index writers, guaranteeing thread safety.
- **Disk Persistence (LSM-Tree):** Memory indexes are periodically flushed to immutable JSON disk segments. A background merge process compacts segments to optimize I/O overhead.
- **LRU Query Caching:** A custom Least Recently Used (LRU) Cache bypasses expensive AST evaluations and vector mathematics for frequent queries, guaranteeing `O(1)` ultra-low latency.
- **Point-in-Time Backups:** Native API and CLI support for compressing the entire cluster (memory and disk) into a snapshot archive for disaster recovery.

### 🌐 Interfacing
- **Sleek Web Frontend:** A beautiful, responsive Single-Page Application (SPA) built with HTML/CSS/JS that interacts directly with the API.
- **Python Client SDK:** An object-oriented `EssaClient` allowing seamless integration into other Python microservices.
- **RESTful API:** Powered by FastAPI for highly scalable node deployments.

---

## 📚 Documentation Directory

EssaSearch comes with comprehensive, enterprise-grade documentation to help you navigate, deploy, and integrate the system.

1. 📖 [User Manual (`USER_MANUAL.md`)](./USER_MANUAL.md)
   - Learn how to use the interactive CLI.
   - Master the advanced AST Query Syntax (AND, OR, NOT, grouping).
   - Understand how Hybrid Search scores are calculated.
2. 🔌 [Integration Guide (`INTEGRATION_GUIDE.md`)](./INTEGRATION_GUIDE.md)
   - Step-by-step instructions on utilizing the Python Client SDK (`client.py`).
   - Detailed API endpoint references (`/search`, `/index`, `/backup`).
3. 🌍 [Master Ecosystem Guide (`ECOSYSTEM_INTEGRATION.md`)](./ECOSYSTEM_INTEGRATION.md)
   - The architectural blueprint for connecting EssaSearch with **EssaDB**, **EssaProxy**, **EssaConnect**, and **EssaCache**.
   - Includes Mermaid diagrams and CDC (Change Data Capture) patterns.

---

## ⚡ Quickstart (Docker)

The fastest way to experience EssaSearch is through Docker. This avoids having to install gigabytes of PyTorch machine-learning dependencies on your host machine.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/EssaSearch.git
cd EssaSearch

# 2. Boot the cluster in the background
docker-compose up -d

# 3. Access the interfaces
```
- **Web UI:** Open [http://localhost:8000](http://localhost:8000) in your browser.
- **API Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

## 💻 Local Development (Python Virtual Env)

If you wish to run the interactive CLI natively, install the project locally:

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -e .

# 3. Start the Server
uvicorn essasearch.server:app --reload

# 4. Run the CLI (in a new terminal tab)
essasearch
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
