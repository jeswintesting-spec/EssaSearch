import re
from typing import List

class Highlighter:
    """
    Generates contextual snippets from documents with highlighted query terms.
    Similar to Google Search result snippets.
    """
    def __init__(self, snippet_length: int = 80):
        self.snippet_length = snippet_length
        
    def generate_snippet(self, text: str, query_terms: List[str]) -> str:
        if not text:
            return ""
        if not query_terms:
            return text[:self.snippet_length] + ("..." if len(text) > self.snippet_length else "")
            
        lower_text = text.lower()
        
        # Find the first occurrence of any query term to center the snippet
        first_match_idx = -1
        for term in query_terms:
            idx = lower_text.find(term.lower())
            if idx != -1:
                if first_match_idx == -1 or idx < first_match_idx:
                    first_match_idx = idx
                    
        if first_match_idx == -1:
            return text[:self.snippet_length] + ("..." if len(text) > self.snippet_length else "")
            
        # Center the snippet around the matched term
        start = max(0, first_match_idx - (self.snippet_length // 2))
        end = min(len(text), start + self.snippet_length)
        
        # Adjust boundaries to not break words if possible
        if start > 0:
            while start < len(text) and text[start] not in (' ', '\n', '\t') and start > 0:
                start -= 1
            if start < len(text) and text[start] in (' ', '\n', '\t'):
                start += 1
                
        if end < len(text):
            while end > start and text[end-1] not in (' ', '\n', '\t') and end < len(text):
                end += 1
                
        snippet = text[start:end].strip()
        prefix = "... " if start > 0 else ""
        suffix = " ..." if end < len(text) else ""
        
        highlighted_snippet = snippet
        for term in query_terms:
            if not term.strip():
                continue
            # Case-insensitive replace with [[term]]
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted_snippet = pattern.sub(lambda m: f"[[{m.group(0)}]]", highlighted_snippet)
            
        return prefix + highlighted_snippet + suffix
