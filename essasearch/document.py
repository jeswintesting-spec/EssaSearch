from typing import Dict, Any, Optional

class Document:
    """
    Represents a single document in the search engine.
    """
    def __init__(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.id = doc_id
        self.content = content
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"<Document id={self.id}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata
        }
