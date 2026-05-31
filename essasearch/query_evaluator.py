from typing import Set, Dict, Any
from essasearch.query_parser import ASTNode, TermNode, AndNode, OrNode, NotNode
from essasearch.analyzer import Analyzer

class QueryEvaluator:
    """
    Evaluates an AST query against the search engine's indexes.
    Returns a set of document IDs that match the query logic.
    """
    def __init__(self, index, segment_manager, mem_documents, analyzer: Analyzer):
        self.index = index
        self.segment_manager = segment_manager
        self.mem_documents = mem_documents
        self.analyzer = analyzer

    def _get_all_doc_ids(self) -> Set[str]:
        doc_ids = set(self.mem_documents.keys())
        if self.segment_manager:
            for segment in self.segment_manager.segments:
                if "documents" in segment:
                    doc_ids.update(segment["documents"].keys())
        return doc_ids

    def evaluate(self, node: ASTNode) -> Set[str]:
        if node is None:
            return set()
            
        if isinstance(node, TermNode):
            # If there's a field (e.g., author:Alice), we must check document metadata
            # Otherwise, use the standard inverted index
            if node.field:
                return self._evaluate_field_term(node.field, node.value)
            else:
                return self._evaluate_content_term(node.value)
                
        elif isinstance(node, AndNode):
            left_docs = self.evaluate(node.left)
            right_docs = self.evaluate(node.right)
            return left_docs.intersection(right_docs)
            
        elif isinstance(node, OrNode):
            left_docs = self.evaluate(node.left)
            right_docs = self.evaluate(node.right)
            return left_docs.union(right_docs)
            
        elif isinstance(node, NotNode):
            all_docs = self._get_all_doc_ids()
            sub_docs = self.evaluate(node.node)
            return all_docs.difference(sub_docs)
            
        raise ValueError(f"Unknown AST Node type: {type(node)}")

    def _evaluate_content_term(self, term: str) -> Set[str]:
        # Analyze the term (lowercase, stem, etc.)
        analyzed_terms = self.analyzer.analyze(term)
        if not analyzed_terms:
            return set()
            
        # For simplicity, if a term analyzes to multiple (e.g., phrase), we AND them
        # But usually a single token yields a single stemmed token
        docs = None
        for t in analyzed_terms:
            t_docs = self.index.get_docs_with_term(t)
            if not t_docs:
                # Typo tolerance / Fuzzy fallback
                fuzzy = self.index.vocabulary.search_fuzzy(t, max_edit_distance=2)
                if fuzzy:
                    t_docs = self.index.get_docs_with_term(fuzzy[0][0])
                else:
                    t_docs = set()
                    
            if docs is None:
                docs = t_docs
            else:
                docs = docs.intersection(t_docs)
                
        return docs or set()

    def _evaluate_field_term(self, field: str, value: str) -> Set[str]:
        """Slow linear scan for field matching, as we don't have a field index."""
        matching_docs = set()
        value = value.lower()
        
        # Check memory docs
        for doc_id, doc in self.mem_documents.items():
            meta = doc.get("metadata", {})
            if meta and str(meta.get(field, "")).lower() == value:
                matching_docs.add(doc_id)
                
        # Check disk segments
        if self.segment_manager:
            for segment in self.segment_manager.segments:
                if "documents" in segment:
                    for doc_id, doc in segment["documents"].items():
                        meta = doc.get("metadata", {})
                        if meta and str(meta.get(field, "")).lower() == value:
                            matching_docs.add(doc_id)
                            
        return matching_docs
