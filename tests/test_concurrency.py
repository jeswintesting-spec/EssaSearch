import pytest
import threading
import time
from essasearch.engine import SearchEngine
import os
import shutil

def setup_module(module):
    if os.path.exists("test_data_concurrent"):
        shutil.rmtree("test_data_concurrent")

def teardown_module(module):
    if os.path.exists("test_data_concurrent"):
        shutil.rmtree("test_data_concurrent")

def test_concurrent_read_write():
    engine = SearchEngine(data_dir="test_data_concurrent")
    
    # Pre-index a document
    engine.index_document("0", "Initial document about dog.")
    
    # Flags and counters for threads
    reads_completed = 0
    writes_completed = 0
    errors = []
    
    # Lock for thread-safe counting
    counter_lock = threading.Lock()

    def reader_thread():
        nonlocal reads_completed
        try:
            for _ in range(50):
                res = engine.search("dog")
                assert res["hits"] >= 1
                with counter_lock:
                    reads_completed += 1
                # Small sleep to simulate work and force interleaving
                time.sleep(0.001)
        except Exception as e:
            errors.append(e)

    def writer_thread(start_idx):
        nonlocal writes_completed
        try:
            for i in range(10):
                doc_id = str(start_idx + i)
                engine.index_document(doc_id, f"Another dog document {doc_id}.")
                with counter_lock:
                    writes_completed += 1
                time.sleep(0.005)
        except Exception as e:
            errors.append(e)

    threads = []
    
    # Spawn 10 readers
    for _ in range(10):
        t = threading.Thread(target=reader_thread)
        threads.append(t)
        
    # Spawn 3 writers
    for i in range(3):
        t = threading.Thread(target=writer_thread, args=(i * 100 + 1,))
        threads.append(t)

    # Start all threads
    for t in threads:
        t.start()
        
    # Wait for all to finish
    for t in threads:
        t.join()
        
    assert not errors, f"Errors occurred during concurrency test: {errors}"
    assert reads_completed == 500, f"Expected 500 reads, got {reads_completed}"
    assert writes_completed == 30, f"Expected 30 writes, got {writes_completed}"
    assert engine.index.total_docs == 31 # 1 initial + 30 written
