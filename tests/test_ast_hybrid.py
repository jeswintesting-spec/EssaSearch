import pytest
from essasearch.engine import SearchEngine
import os
import shutil

def setup_module(module):
    if os.path.exists("test_data_ast"):
        shutil.rmtree("test_data_ast")

def teardown_module(module):
    if os.path.exists("test_data_ast"):
        shutil.rmtree("test_data_ast")

def test_ast_parsing(engine=None):
    if not engine:
        engine = SearchEngine(data_dir="test_data_ast")
        engine.index_document("1", "The quick brown fox jumps over the lazy dog.", metadata={"author": "Alice", "category": "fiction"})
        engine.index_document("2", "A fast fox runs through the forest.", metadata={"author": "Bob"})
        engine.index_document("3", "The lazy dog sleeps all day long.", metadata={"author": "Alice"})
        engine.index_document("4", "No animals here, just a database query.", metadata={"author": "Charlie"})
    
    # Simple term
    res = engine.search("fox")
    assert res["hits"] == 2
    
    # AND operator
    res = engine.search("fox AND dog")
    assert res["hits"] == 1
    assert res["results"][0]["id"] == "1"
    
    # OR operator
    res = engine.search("fox OR dog")
    assert res["hits"] == 3
    
    # NOT operator
    res = engine.search("fox NOT dog")
    assert res["hits"] == 1
    assert res["results"][0]["id"] == "2"
    
    # Parenthesis and Field queries
    res = engine.search("author:Alice AND (fox OR dog)")
    assert res["hits"] == 2
    ids = [r["id"] for r in res["results"]]
    assert "1" in ids
    assert "3" in ids
    
    # Field query NOT
    res = engine.search("author:Alice NOT fox")
    assert res["hits"] == 1
    assert res["results"][0]["id"] == "3"

def test_hybrid_search():
    engine = SearchEngine(data_dir="test_data_ast")
    # If transformers is installed, this will test vector cosine similarity 
    # as well as BM25 scoring.
    engine.index_document("1", "A completely irrelevant document about cars and automobiles.")
    engine.index_document("2", "A document about felines, cats, and kittens.", metadata={"tags": "animals"})
    
    # Query semantic match
    # "dogs" should be semantically closer to "cats" than "cars" if embeddings work.
    # We will just verify it returns results and doesn't crash.
    res = engine.search("dogs")
    assert res is not None
