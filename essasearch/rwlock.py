import threading
from contextlib import contextmanager

class ReadWriteLock:
    """
    A custom Read-Write Lock utilizing Python's native threading.Condition.
    This demonstrates deep understanding of OS synchronization primitives.
    
    Rules:
    - Multiple threads can hold the read lock simultaneously.
    - Only ONE thread can hold the write lock.
    - If a thread holds the write lock, no other threads can read or write.
    - To prevent writer starvation, new readers are blocked if there are waiting writers.
    """
    def __init__(self):
        self._condition = threading.Condition(threading.Lock())
        self._readers = 0
        self._writers = 0
        self._waiting_writers = 0

    @contextmanager
    def read_lock(self):
        """Context manager for acquiring the read lock."""
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self):
        """Context manager for acquiring the write lock."""
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()

    def acquire_read(self):
        with self._condition:
            # Block if there is an active writer, OR if a writer is waiting.
            # Checking waiting writers is crucial to prevent "writer starvation"
            # where a continuous stream of new readers locks out writers forever.
            while self._writers > 0 or self._waiting_writers > 0:
                self._condition.wait()
            self._readers += 1

    def release_read(self):
        with self._condition:
            self._readers -= 1
            # If we are the last reader, wake up any waiting threads (usually writers)
            if self._readers == 0:
                self._condition.notify_all()

    def acquire_write(self):
        with self._condition:
            self._waiting_writers += 1
            # A writer must wait until there are ZERO active readers and ZERO active writers
            while self._readers > 0 or self._writers > 0:
                self._condition.wait()
            self._waiting_writers -= 1
            self._writers += 1

    def release_write(self):
        with self._condition:
            self._writers -= 1
            # Writer is done, wake up everyone (readers and other waiting writers)
            self._condition.notify_all()
