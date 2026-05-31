from typing import Dict, List, Set
from collections import defaultdict
import math

from essasearch.trie import Trie

class InvertedIndex:
    """
    The core Inverted Index data structure.
    Maps terms -> {doc_id: term_frequency}
    Also keeps track of document lengths and average document length for BM25.
    """
    def __init__(self, segment_manager=None):
        # term -> {doc_id: term_frequency}
        self.index: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # doc_id -> number of terms in the document
        self.doc_lengths: Dict[str, int] = {}
        
        # Total number of documents
        self.total_docs: int = 0
        
        # Total length of all documents combined
        self.total_length: int = 0
        
        # Vocabulary Trie for fast fuzzy search and typo tolerance
        self.vocabulary = Trie()
        
        # Disk segment manager
        self.segment_manager = segment_manager
        
        # Load vocabulary from segments if they exist
        if self.segment_manager:
            for segment in self.segment_manager.segments:
                for term in segment["index"]:
                    self.vocabulary.insert(term)

    def add_document(self, doc_id: str, terms: List[str]):
        """
        Add a document's terms to the in-memory inverted index.
        """
        if doc_id in self.doc_lengths:
            return
            
        doc_length = len(terms)
        self.doc_lengths[doc_id] = doc_length
        self.total_docs += 1
        self.total_length += doc_length

        for term in terms:
            self.index[term][doc_id] += 1
            # Insert the term into our Trie for fuzzy matching
            self.vocabulary.insert(term)
            
    def _get_global_postings(self, term: str) -> Dict[str, int]:
        postings = {}
        if self.segment_manager:
            postings.update(self.segment_manager.get_term_postings(term))
        postings.update(self.index.get(term, {}))
        return postings

    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """Get the frequency of a term in a specific document."""
        return self._get_global_postings(term).get(doc_id, 0)

    def get_document_frequency(self, term: str) -> int:
        """Get the number of documents containing the term."""
        return len(self._get_global_postings(term))

    def get_docs_with_term(self, term: str) -> Set[str]:
        """Get all document IDs that contain the given term."""
        return set(self._get_global_postings(term).keys())

    def get_avg_doc_length(self) -> float:
        """Get the average document length across memory and disk."""
        global_total_docs = self.total_docs
        global_total_length = self.total_length
        if self.segment_manager:
            stats = self.segment_manager.get_global_stats()
            global_total_docs += stats["total_docs"]
            global_total_length += stats["total_length"]
            
        if global_total_docs == 0:
            return 0.0
        return global_total_length / global_total_docs
        
    def get_doc_length(self, doc_id: str) -> int:
        """Get the length of a specific document."""
        if doc_id in self.doc_lengths:
            return self.doc_lengths[doc_id]
        if self.segment_manager:
            stats = self.segment_manager.get_global_stats()
            return stats["doc_lengths"].get(doc_id, 0)
        return 0

    def reset_memory(self):
        """Clear the in-memory index after flushing to disk."""
        self.index = defaultdict(lambda: defaultdict(int))
        self.doc_lengths = {}
        self.total_docs = 0
        self.total_length = 0
