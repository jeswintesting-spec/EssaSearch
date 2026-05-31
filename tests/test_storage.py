import pytest
import os
import shutil
from essasearch.engine import SearchEngine

def setup_module(module):
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")

def teardown_module(module):
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")

def test_flush_and_merge():
    engine = SearchEngine(data_dir="test_data")
    
    # Index some documents
    engine.index_document("1", "First document about search.")
    engine.index_document("2", "Second document about databases.")
    
    assert engine.index.total_docs == 2
    
    # Flush to disk (segment 1)
    engine.flush()
    assert engine.index.total_docs == 0  # Memory cleared
    assert len(engine.segment_manager.segments) == 1
    
    # Search should still work using disk segment
    res = engine.search("search")
    assert res["hits"] == 1
    assert res["results"][0]["id"] == "1"
    
    # Index more documents (in memory)
    engine.index_document("3", "Third document about search and AI.")
    engine.index_document("4", "Fourth document.")
    
    # Search should use both memory and disk
    res = engine.search("search")
    assert res["hits"] == 2
    
    # Flush again (segment 2)
    engine.flush()
    assert len(engine.segment_manager.segments) == 2
    
    # Merge segments
    engine.merge()
    assert len(engine.segment_manager.segments) == 1
    
    # Search should still work identically
    res = engine.search("search")
    assert res["hits"] == 2
