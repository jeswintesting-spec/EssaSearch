import math
from typing import List, Dict, Tuple
from essasearch.index import InvertedIndex

class BM25Ranker:
    """
    Implements the Okapi BM25 ranking algorithm.
    This algorithm ranks documents based on term frequencies and inverse document frequencies,
    accounting for document length normalization.
    """
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1
        self.b = b

    def _calculate_idf(self, doc_freq: int, total_docs: int) -> float:
        """
        Calculate Inverse Document Frequency (IDF).
        Using the standard formula that avoids negative values.
        """
        # IDF(q) = ln( (N - n(q) + 0.5) / (n(q) + 0.5) + 1 )
        numerator = total_docs - doc_freq + 0.5
        denominator = doc_freq + 0.5
        return math.log(numerator / denominator + 1.0)

    def score(self, query_terms: List[str], doc_ids: set) -> List[Tuple[str, float]]:
        """
        Score a set of documents for the given query terms.
        Returns a list of (doc_id, score) tuples, sorted by score descending.
        """
        scores: Dict[str, float] = {doc_id: 0.0 for doc_id in doc_ids}
        total_docs = self.index.total_docs
        avg_doc_len = self.index.get_avg_doc_length()

        for term in query_terms:
            doc_freq = self.index.get_document_frequency(term)
            if doc_freq == 0:
                continue

            idf = self._calculate_idf(doc_freq, total_docs)

            for doc_id in doc_ids:
                tf = self.index.get_term_frequency(term, doc_id)
                if tf == 0:
                    continue

                doc_len = self.index.get_doc_length(doc_id)
                
                # BM25 Term Score Formula
                # TF_term = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_doc_len)))
                length_norm = 1.0 - self.b + self.b * (doc_len / avg_doc_len)
                tf_term = (tf * (self.k1 + 1.0)) / (tf + self.k1 * length_norm)
                
                scores[doc_id] += idf * tf_term

        # Sort by score descending
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores
