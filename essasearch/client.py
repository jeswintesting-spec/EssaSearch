import requests
from typing import Dict, Any, Optional

class EssaClient:
    """
    Python SDK for interacting with the EssaSearch cluster.
    Provides a clean, object-oriented interface for indexing, searching, and managing the cluster.
    """
    def __init__(self, host: str = "http://localhost:8000"):
        self.host = host.rstrip("/")

    def index(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Index a new document."""
        url = f"{self.host}/index"
        payload = {"id": doc_id, "content": content, "metadata": metadata or {}}
        res = requests.post(url, json=payload)
        return res.status_code == 200

    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search the cluster using the AST parser and hybrid semantic embeddings."""
        url = f"{self.host}/search"
        payload = {"query": query, "limit": limit}
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()

    def get_stats(self) -> Dict[str, Any]:
        """Fetch engine statistics (memory vs disk, cache hit ratio, etc)."""
        url = f"{self.host}/stats"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()

    def flush(self) -> bool:
        """Force flush in-memory documents to immutable disk segments."""
        url = f"{self.host}/flush"
        res = requests.post(url)
        return res.status_code == 200

    def merge(self) -> bool:
        """Trigger LSM-Tree segment compaction."""
        url = f"{self.host}/merge"
        res = requests.post(url)
        return res.status_code == 200

    def backup(self, filename: str) -> bool:
        """Create a point-in-time snapshot archive of the cluster."""
        url = f"{self.host}/backup"
        res = requests.post(url, json={"filename": filename})
        return res.status_code == 200

    def restore(self, filename: str) -> bool:
        """Restore the cluster from a backup archive."""
        url = f"{self.host}/restore"
        res = requests.post(url, json={"filename": filename})
        return res.status_code == 200
