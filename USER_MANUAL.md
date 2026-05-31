# 📖 EssaSearch User Manual

Welcome to **EssaSearch**. This manual is designed for end-users and administrators operating the search engine. It covers everything from writing advanced search queries using our custom Abstract Syntax Tree (AST) to managing disk persistence and creating cluster backups.

---

## 🖥️ 1. Accessing the Interfaces

EssaSearch provides two primary ways for users to interact with the engine:

### The Web Interface (Graphical UI)
The easiest way to experience the engine.
1. Ensure the server is running (`docker-compose up -d` or `uvicorn essasearch.server:app`).
2. Open your web browser and navigate to `http://localhost:8000`.
3. Use the search bar to run queries and view highlighted contextual snippets instantly.

### The Interactive CLI (Terminal UI)
For power users and administrators who want to view deep cluster metrics.
1. Open a new terminal window.
2. Run the command: `essasearch`.
3. You will be greeted with the main menu where you can press a number `[1-8]` to trigger an action.

---

## 🔎 2. Writing Advanced Search Queries

Because EssaSearch compiles your query string into an **Abstract Syntax Tree (AST)** before execution, you are not limited to simple keyword searches. You can use advanced boolean logic to pinpoint exactly what you are looking for.

### Basic Keyword Search
If you type multiple words without operators, the engine treats them as an implicit `OR`.
* **Query:** `fast fox`
* **Result:** Returns documents containing *either* "fast" or "fox".

### Boolean Operators
Operators must be written in **UPPERCASE**.
* **AND:** `fox AND dog` (Returns documents containing *both* words).
* **OR:** `fox OR dog` (Returns documents containing *either* word).
* **NOT:** `fox NOT dog` (Returns documents containing "fox", but completely excludes any document containing "dog").

### Grouping and Precedence
You can use parentheses `()` to group logic, exactly like mathematical equations.
* **Query:** `(fast OR quick) AND fox`
* **Result:** Finds documents that have the word "fox", and *at least one* of the words "fast" or "quick".

### Field-Specific Searching
If you indexed a document with metadata (e.g., `{"author": "Alice"}`), you can search directly inside that field.
* **Query:** `author:Alice AND fox`
* **Result:** Only returns documents written by Alice that contain the word "fox".

---

## 🤖 3. How "Hybrid Search" Works

EssaSearch doesn't just look for exact word matches; it understands the *meaning* of your query. 

When you search for something, the engine calculates two separate scores behind the scenes:
1. **The Keyword Score (BM25):** Calculates exact word matches, giving higher weight to rare words and shorter documents.
2. **The Semantic Score (Vector Embeddings):** The engine uses `sentence-transformers` to convert your query into a 384-dimensional mathematical vector. It calculates the *Cosine Similarity* against the documents in the database. (e.g., A search for "dogs" will naturally match a document about "cats and felines" because their vectors are grouped closely together in semantic space).

The engine automatically fuses these scores together `(0.5 * BM25 + 0.5 * Vector)` and returns the list sorted by the highest hybrid relevance.

---

## 💡 4. Typo Tolerance and Fuzzy Matching

If you make a spelling mistake, EssaSearch will catch it.
* **Query:** `pterdactyl` (Notice the missing 'o')
* **Result:** The engine uses a custom **Prefix Tree (Trie)** combined with the **Levenshtein Distance Algorithm**. It scans its vocabulary, realizes `pterodactyl` is only 1 edit distance away, and seamlessly returns results for the correct spelling without you having to retype the query!

---

## 💾 5. Managing Disk Persistence

EssaSearch operates using an **LSM-Tree Architecture**. This means data is written to memory first for blindingly fast writes, and later flushed to disk.

As an administrator using the CLI, you have access to two critical commands:

### `[4] Flush Memory to Disk`
Forces the engine to take everything currently in RAM and write it to an immutable JSON "Segment" on your hard drive (inside the `data/` folder). Note: The engine automatically does this if memory exceeds 1,000 documents, but you can force it manually here.

### `[5] Merge Disk Segments`
Over time, flushing creates dozens of small files on your hard drive. This can slow down search queries because the engine has to check every single file.
Clicking "Merge" triggers a compaction process. It takes all the small segment files, combines them, removes deleted documents, and creates one massive, highly-optimized segment file.

---

## 🛡️ 6. Disaster Recovery (Backup & Restore)

It is critical to backup your search cluster before making major architectural changes or server migrations. 

Using the CLI:
* **`[6] Backup Cluster`:** Safely pauses all active writes, flushes all memory to disk, and compresses your entire database into a single, portable `.zip` file.
* **`[7] Restore Cluster from Backup`:** Warning: This is a destructive action. It deletes your current live data, unpacks the `.zip` backup archive you specify, and instantly reloads the search engine to the exact state of the backup.

---

### Need API Access?
If you are a developer looking to interact with EssaSearch programmatically via HTTP requests or the Python SDK, please refer to the [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md).
