from typing import List
import math

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: sentence-transformers or numpy not installed. Vector search disabled.")

class VectorEmbedder:
    """
    Handles generation of semantic embeddings using a lightweight local neural network.
    This enables hybrid search (Semantic + Keyword relevance).
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = None
        if HAS_TRANSFORMERS:
            # Load a small, fast model ideal for semantic search
            self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> List[float]:
        """Convert text into a dense vector embedding."""
        if not self.model:
            return []
        
        # encode returns a numpy array, we convert to list for easy JSON serialization
        vector = self.model.encode(text)
        return vector.tolist()

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute the cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
            
        if HAS_TRANSFORMERS:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(np.dot(v1, v2) / (norm1 * norm2))
        else:
            # Fallback when numpy is not available
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(b * b for b in vec2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot_product / (norm1 * norm2)
