from collections import OrderedDict
from typing import Any, Optional

class LRUCache:
    """
    Least Recently Used (LRU) Cache.
    Stores the most frequent search queries to prevent re-evaluating the AST
    and re-computing Vector Embeddings on identical requests.
    """
    def __init__(self, capacity: int = 100):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            self.misses += 1
            return None
        # Move to end to mark as most recently used
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Pop the least recently used (first item)
            self.cache.popitem(last=False)
            
    def invalidate(self):
        """Clear the cache. Called when index is mutated."""
        self.cache.clear()
        
    def get_stats(self) -> dict:
        total = self.hits + self.misses
        hit_ratio = (self.hits / total) if total > 0 else 0.0
        return {
            "capacity": self.capacity,
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": round(hit_ratio, 4)
        }
