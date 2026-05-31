import pytest
from essasearch.engine import SearchEngine

@pytest.fixture
def engine():
    se = SearchEngine()
    # Index some test documents
    se.index_document("1", "The quick brown fox jumps over the lazy dog.", {"author": "Alice"})
    se.index_document("2", "A fast brown fox leaps over a sleepy dog.", {"author": "Bob"})
    se.index_document("3", "The dog is lazy but the fox is quick and smart.", {"author": "Charlie"})
    se.index_document("4", "No foxes or dogs here, just a running cat.", {"author": "Dave"})
    se.index_document("5", "Quick foxes are quick. Dogs are dogs.", {"author": "Eve"})
    return se

def test_tokenization_and_stemming(engine):
    # 'foxes' should stem to 'fox', 'running' to 'run'
    assert "fox" in engine.analyzer.analyze("foxes")
    assert "run" in engine.analyzer.analyze("running")
    # Stop words should be removed
    assert "the" not in engine.analyzer.analyze("the quick fox")

def test_search_exact_match(engine):
    output = engine.search("lazy")
    results = output["results"]
    assert len(results) == 2
    # Docs 1 and 3 contain 'lazy'
    doc_ids = [r["id"] for r in results]
    assert "1" in doc_ids
    assert "3" in doc_ids

def test_search_stemmed_match(engine):
    # Searching for 'foxes' should match 'fox'
    output = engine.search("foxes")
    results = output["results"]
    assert len(results) > 0
    doc_ids = [r["id"] for r in results]
    assert "1" in doc_ids  # 'fox'
    assert "4" in doc_ids  # 'foxes'
    assert "5" in doc_ids  # 'foxes'

def test_bm25_ranking(engine):
    # 'quick' appears twice in doc 5, once in doc 1, once in doc 3.
    # Doc 5 is shorter than Doc 3, so its term frequency and length norm should rank it highest.
    output = engine.search("quick")
    results = output["results"]
    assert len(results) == 3
    
    # Doc 5 has highest TF for 'quick' (2 times)
    assert results[0]["id"] == "5"

def test_empty_search(engine):
    output = engine.search("pterodactyl")
    assert len(output["results"]) == 0

def test_fuzzy_search(engine):
    # Typo: "quik" instead of "quick"
    output = engine.search("quik")
    
    # It should still find documents matching "quick" despite the typo
    results = output["results"]
    assert len(results) == 3  # Same as searching for "quick"
    assert results[0]["id"] == "5"

def test_stats(engine):
    assert engine.index.total_docs == 5
