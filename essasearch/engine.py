from typing import List, Dict, Any, Optional
from essasearch.document import Document
from essasearch.analyzer import Analyzer
from essasearch.index import InvertedIndex
from essasearch.ranker import BM25Ranker
from essasearch.storage import SegmentManager
from essasearch.rwlock import ReadWriteLock
from essasearch.query_parser import QueryParser
from essasearch.query_evaluator import QueryEvaluator
from essasearch.vector_search import VectorEmbedder
from essasearch.cache import LRUCache
from essasearch.highlighter import Highlighter

class SearchEngine:
    """
    The main facade for EssaSearch.
    Coordinates the Analyzer, InvertedIndex, and Ranker.
    Includes thread-safe Read-Write concurrency.
    """
    def __init__(self, data_dir: str = "data"):
        self.rw_lock = ReadWriteLock()
        self.segment_manager = SegmentManager(data_dir=data_dir)
        self.analyzer = Analyzer()
        self.index = InvertedIndex(segment_manager=self.segment_manager)
        self.ranker = BM25Ranker(self.index)
        self.parser = QueryParser()
        self.embedder = VectorEmbedder()
        self.cache = LRUCache()
        self.highlighter = Highlighter()
        
        # In-memory document store (doc_id -> Document dict format)
        self.mem_documents: Dict[str, Dict[str, Any]] = {}

    def flush(self):
        """Force flush of in-memory structures to disk segment."""
        with self.rw_lock.write_lock():
            self.cache.invalidate()
            if self.index.total_docs > 0:
                self.segment_manager.flush(self.index, self.mem_documents)
                self.index.reset_memory()
                self.mem_documents = {}

    def merge(self):
        """Merge all disk segments."""
        with self.rw_lock.write_lock():
            self.cache.invalidate()
            self.segment_manager.merge_segments()

    def index_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Process and index a document.
        Uses write lock to ensure thread safety during mutation.
        """
        metadata = metadata or {}
        doc = Document(doc_id, content, metadata)
        
        # Generate Vector Embedding for Semantic Search
        embedding = self.embedder.embed_text(content)
        if embedding:
            doc.metadata["_embedding"] = embedding
            
        with self.rw_lock.write_lock():
            self.cache.invalidate()
            self.mem_documents[doc_id] = doc.to_dict()
            
            # 1. Analyze text (tokenize, stop-words, stem)
            terms = self.analyzer.analyze(content)
            
            # 2. Add to inverted index
            self.index.add_document(doc_id, terms)
            
            # Auto-flush if memory index gets large
            if self.index.total_docs >= 1000:
                self._flush_unlocked()
                
    def _flush_unlocked(self):
        if self.index.total_docs > 0:
            self.segment_manager.flush(self.index, self.mem_documents)
            self.index.reset_memory()
            self.mem_documents = {}

    def search(self, query: str, limit: int = 10, max_edit_distance: int = 2) -> Dict[str, Any]:
        """
        Search for documents matching the query.
        Returns a dict containing document info, rank score, and potentially corrected query terms.
        Uses read lock to allow highly concurrent searches while blocking writers.
        """
        cache_key = f"{query}:{limit}:{max_edit_distance}"
        
        with self.rw_lock.read_lock():
            # Check Cache First
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # 1. Parse Query into AST
            ast_node = None
            try:
                ast_node = self.parser.parse(query)
            except Exception as e:
                pass
                
            evaluator = QueryEvaluator(self.index, self.segment_manager, self.mem_documents, self.analyzer)
            matching_doc_ids = set()
            
            # Extract terms for BM25 and Highlighting
            query_terms = self.analyzer.analyze(query)
            
            if ast_node:
                matching_doc_ids = evaluator.evaluate(ast_node)
            else:
                for term in query_terms:
                    docs = self.index.get_docs_with_term(term)
                    if docs:
                        matching_doc_ids.update(docs)
                    else:
                        fuzzy = self.index.vocabulary.search_fuzzy(term, max_edit_distance)
                        if fuzzy:
                            matching_doc_ids.update(self.index.get_docs_with_term(fuzzy[0][0]))
            
            if not matching_doc_ids:
                res = {"query": query, "hits": 0, "results": []}
                self.cache.put(cache_key, res)
                return res
            
            # 2. BM25 Ranking
            bm25_results = dict(self.ranker.score(query_terms, matching_doc_ids))
            max_bm25 = max(bm25_results.values()) if bm25_results else 1.0
            if max_bm25 == 0:
                max_bm25 = 1.0

            # 3. Vector Embedding (Semantic Search)
            query_embedding = self.embedder.embed_text(query)
            
            final_scores = {}
            for doc_id in matching_doc_ids:
                doc_dict = self.mem_documents.get(doc_id) or self.segment_manager.get_document(doc_id)
                if not doc_dict:
                    continue
                    
                bm25_score = bm25_results.get(doc_id, 0.0) / max_bm25
                vector_score = 0.0
                doc_embedding = doc_dict.get("metadata", {}).get("_embedding")
                if query_embedding and doc_embedding:
                    vector_score = self.embedder.cosine_similarity(query_embedding, doc_embedding)
                    
                alpha = 0.5 if (query_embedding and doc_embedding) else 1.0
                final_score = (alpha * bm25_score) + ((1 - alpha) * vector_score)
                final_scores[doc_id] = final_score

            ranked_doc_ids = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)
            
            # 4. Format results & Highlight Snippets
            results = []
            for doc_id in ranked_doc_ids[:limit]:
                score = final_scores[doc_id]
                doc_dict = self.mem_documents.get(doc_id)
                if not doc_dict:
                    doc_dict = self.segment_manager.get_document(doc_id)
                    
                if doc_dict:
                    meta_copy = dict(doc_dict.get("metadata", {}))
                    meta_copy.pop("_embedding", None)
                    
                    # Generate Contextual Snippet
                    content = doc_dict["content"]
                    snippet = self.highlighter.generate_snippet(content, query_terms)
                    
                    results.append({
                        "id": doc_dict["id"],
                        "score": score,
                        "content": snippet,
                        "metadata": meta_copy
                    })
                
            final_res = {
                "query": query,
                "hits": len(results),
                "results": results
            }
            
            # Save to Cache
            self.cache.put(cache_key, final_res)
            return final_res

    def get_stats(self) -> Dict[str, Any]:
        """Get global stats across memory and disk."""
        with self.rw_lock.read_lock():
            disk_stats = self.segment_manager.get_global_stats()
            
            # Calculate unique terms
            unique_terms = set(self.index.index.keys())
            for segment in self.segment_manager.segments:
                unique_terms.update(segment["index"].keys())
                
            return {
                "total_documents": self.index.total_docs + disk_stats["total_docs"],
                "total_terms": len(unique_terms),
                "memory_documents": self.index.total_docs,
                "disk_documents": disk_stats["total_docs"],
                "active_segments": len(self.segment_manager.segments),
                "cache_stats": self.cache.get_stats()
            }

    def create_backup(self, filepath: str) -> str:
        """
        Creates a point-in-time snapshot of the entire search engine cluster.
        Forces a flush to disk, then compresses the data directory into an archive.
        """
        import shutil
        import os
        
        # 1. Flush memory to disk to ensure data consistency
        self.flush()
        
        with self.rw_lock.write_lock():
            # 2. Archive the entire data directory
            # shutil.make_archive adds the extension automatically (e.g., .zip)
            base_name = filepath.replace('.zip', '')
            archive_path = shutil.make_archive(base_name, 'zip', self.segment_manager.data_dir)
            return archive_path

    def restore_backup(self, filepath: str):
        """
        Restores the search engine cluster from a backup archive.
        Overwrites existing data.
        """
        import shutil
        import os
        
        with self.rw_lock.write_lock():
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Backup file not found: {filepath}")
                
            # 1. Clear memory and cache
            self.mem_documents.clear()
            self.index.reset_memory()
            self.cache.invalidate()
            
            # 2. Empty existing data directory
            for f in os.listdir(self.segment_manager.data_dir):
                os.remove(os.path.join(self.segment_manager.data_dir, f))
                
            # 3. Extract the backup archive into the data directory
            shutil.unpack_archive(filepath, self.segment_manager.data_dir, 'zip')
            
            # 4. Reload segment manager
            self.segment_manager.load_all_segments()
