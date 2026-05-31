import json
import os
import glob
from typing import Dict, List, Set, Any
from essasearch.index import InvertedIndex

class SegmentManager:
    """
    Manages Lucene-style disk segments.
    Provides functionality to flush in-memory indexes to immutable disk segments,
    and merge multiple smaller segments into a single optimized segment.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.segments: List[Dict[str, Any]] = []
        self.segment_counter = 0
        self.load_all_segments()

    def load_all_segments(self):
        """Load all existing segments from disk into memory."""
        self.segments = []
        files = sorted(glob.glob(os.path.join(self.data_dir, "segment_*.json")))
        for f in files:
            with open(f, 'r') as file:
                self.segments.append(json.load(file))
        if files:
            # Extract highest counter
            latest_file = files[-1]
            basename = os.path.basename(latest_file)
            # segment_X.json
            self.segment_counter = int(basename.split('_')[1].split('.')[0])

    def flush(self, mem_index: InvertedIndex, mem_documents: Dict[str, Any]):
        """
        Flush the in-memory Inverted Index and raw documents to an immutable disk segment.
        """
        if mem_index.total_docs == 0:
            return

        self.segment_counter += 1
        segment_path = os.path.join(self.data_dir, f"segment_{self.segment_counter}.json")
        
        segment_data = {
            "id": self.segment_counter,
            "index": mem_index.index,
            "doc_lengths": mem_index.doc_lengths,
            "total_docs": mem_index.total_docs,
            "total_length": mem_index.total_length,
            "documents": mem_documents
        }

        with open(segment_path, 'w') as f:
            json.dump(segment_data, f)

        self.segments.append(segment_data)

    def merge_segments(self):
        """
        LSM-Tree style Merge: Combine all existing segments into a single optimized segment.
        Reduces fragmentation and improves search speed.
        """
        if len(self.segments) <= 1:
            return # Nothing to merge

        merged_index: Dict[str, Dict[str, int]] = {}
        merged_doc_lengths: Dict[str, int] = {}
        merged_documents = {}
        merged_total_docs = 0
        merged_total_length = 0

        # Merge all data
        for segment in self.segments:
            merged_total_docs += segment["total_docs"]
            merged_total_length += segment["total_length"]
            merged_doc_lengths.update(segment["doc_lengths"])
            if "documents" in segment:
                merged_documents.update(segment["documents"])
            
            for term, postings in segment["index"].items():
                if term not in merged_index:
                    merged_index[term] = {}
                # Update postings
                for doc_id, tf in postings.items():
                    merged_index[term][doc_id] = tf

        # Create new optimized segment
        self.segment_counter += 1
        merged_path = os.path.join(self.data_dir, f"segment_{self.segment_counter}_merged.json")
        
        merged_data = {
            "id": self.segment_counter,
            "index": merged_index,
            "doc_lengths": merged_doc_lengths,
            "total_docs": merged_total_docs,
            "total_length": merged_total_length,
            "documents": merged_documents
        }

        with open(merged_path, 'w') as f:
            json.dump(merged_data, f)

        # Delete old segments
        old_files = glob.glob(os.path.join(self.data_dir, "segment_*.json"))
        for f in old_files:
            if f != merged_path:
                os.remove(f)

        self.segments = [merged_data]

    def get_term_postings(self, term: str) -> Dict[str, int]:
        """Get postings for a term across all segments."""
        postings = {}
        for segment in self.segments:
            if term in segment["index"]:
                postings.update(segment["index"][term])
        return postings

    def get_global_stats(self) -> Dict[str, int]:
        """Get combined stats across all segments."""
        total_docs = sum(s["total_docs"] for s in self.segments)
        total_length = sum(s["total_length"] for s in self.segments)
        
        # Combine doc lengths
        doc_lengths = {}
        for s in self.segments:
            doc_lengths.update(s["doc_lengths"])
            
        return {
            "total_docs": total_docs,
            "total_length": total_length,
            "doc_lengths": doc_lengths
        }

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get raw document by ID from segments."""
        for segment in self.segments:
            if "documents" in segment and doc_id in segment["documents"]:
                return segment["documents"][doc_id]
        return None
