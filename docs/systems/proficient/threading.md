---
title: Threading
description: Threads, locks, race conditions, synchronization primitives and the GIL
---

# Threading <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../../core/beginner/functions/">Functions</a></span>
  </div>
</div>

---

## When to use threads

| Workload | Use threads? | Why |
|---|---|---|
| Network I/O (HTTP, DB) | **Yes** | GIL released during I/O |
| File I/O | **Yes** | GIL released during disk ops |
| CPU computation | **No** | GIL prevents parallel execution |
| Shared-memory concurrency | **Yes** | Simpler than multiprocessing |

---

## Basic threading

```python
import threading
import time

def download(url, delay):
    print(f"  [{threading.current_thread().name}] Starting {url}")
    time.sleep(delay)   # simulate network I/O
    print(f"  [{threading.current_thread().name}] Done {url}")
    return f"Data from {url}"

# Sequential — slow
start = time.perf_counter()
for url in ["api/users", "api/posts", "api/comments"]:
    download(url, 1)
print(f"Sequential: {time.perf_counter() - start:.2f}s")   # ~3s

# Threaded — fast
start = time.perf_counter()
threads = []
for url in ["api/users", "api/posts", "api/comments"]:
    t = threading.Thread(target=download, args=(url, 1), name=f"Worker-{url}")
    threads.append(t)
    t.start()

for t in threads:
    t.join()   # wait for all to finish
print(f"Threaded: {time.perf_counter() - start:.2f}s")   # ~1s
```

---

## ThreadPoolExecutor (recommended API)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def fetch_data(url):
    time.sleep(1)   # simulate I/O
    return f"Result from {url}"

urls = [f"https://api.example.com/page/{i}" for i in range(10)]

# Submit tasks and collect results
with ThreadPoolExecutor(max_workers=5) as executor:
    # Method 1: map (ordered results)
    results = list(executor.map(fetch_data, urls))
    print(results)

    # Method 2: submit (futures — unordered, more control)
    futures = {executor.submit(fetch_data, url): url for url in urls}
    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result(timeout=5)
            print(f"  {url}: {result}")
        except Exception as exc:
            print(f"  {url} failed: {exc}")
```

---

## Race conditions

```python
import threading

# UNSAFE — race condition
counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1   # READ → ADD → WRITE (not atomic!)

threads = [threading.Thread(target=increment) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()

print(f"Expected: 4,000,000")
print(f"Actual:   {counter:,}")   # likely < 4,000,000!
# Race: thread A reads 5, thread B reads 5, both write 6 (lost update)
```

---

## Locks

```python
import threading

counter = 0
lock = threading.Lock()

def safe_increment():
    global counter
    for _ in range(1_000_000):
        with lock:          # acquire → release (context manager)
            counter += 1    # only one thread at a time

threads = [threading.Thread(target=safe_increment) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(f"Result: {counter:,}")   # exactly 4,000,000
```

### RLock (re-entrant lock)

```python
rlock = threading.RLock()

def recursive_function(n):
    with rlock:   # same thread can acquire multiple times
        if n > 0:
            recursive_function(n - 1)

# Regular Lock would deadlock here — RLock handles it
```

---

## Other synchronization primitives

### Semaphore — limit concurrent access

```python
import threading
import time

# Only 3 threads can access the resource simultaneously
semaphore = threading.Semaphore(3)

def limited_access(name):
    with semaphore:
        print(f"  {name} acquired (at {time.strftime('%H:%M:%S')})")
        time.sleep(2)
    print(f"  {name} released")

threads = [threading.Thread(target=limited_access, args=(f"Worker-{i}",)) for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()
# Only 3 "acquired" messages at a time
```

### Event — signal between threads

```python
import threading
import time

ready = threading.Event()

def producer():
    print("  Producer: preparing data...")
    time.sleep(2)
    print("  Producer: data ready!")
    ready.set()   # signal consumers

def consumer(name):
    print(f"  {name}: waiting for data...")
    ready.wait()   # blocks until set()
    print(f"  {name}: got data, processing!")

threads = [
    threading.Thread(target=producer),
    threading.Thread(target=consumer, args=("Consumer-1",)),
    threading.Thread(target=consumer, args=("Consumer-2",)),
]
for t in threads: t.start()
for t in threads: t.join()
```

### Condition — complex signaling

```python
import threading
import time
from collections import deque

buffer = deque(maxlen=5)
condition = threading.Condition()

def producer():
    for i in range(20):
        with condition:
            while len(buffer) >= 5:
                condition.wait()   # buffer full — wait
            buffer.append(i)
            print(f"  Produced: {i} (buffer: {list(buffer)})")
            condition.notify_all()   # wake consumers
        time.sleep(0.1)

def consumer(name):
    while True:
        with condition:
            while len(buffer) == 0:
                condition.wait()   # buffer empty — wait
            item = buffer.popleft()
            print(f"  {name} consumed: {item}")
            condition.notify_all()   # wake producer
        time.sleep(0.2)
```

### Barrier — synchronize N threads at a point

```python
import threading

barrier = threading.Barrier(3)   # wait for 3 threads

def worker(name):
    print(f"  {name}: phase 1 done")
    barrier.wait()   # blocks until all 3 arrive
    print(f"  {name}: phase 2 starting")

threads = [threading.Thread(target=worker, args=(f"W{i}",)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()
# All "phase 2" messages appear after all "phase 1" messages
```

---

## Thread-safe data structures

```python
import queue
import threading

# queue.Queue is thread-safe (built-in locking)
q = queue.Queue(maxsize=10)

def producer():
    for i in range(20):
        q.put(i)   # blocks if full
    q.put(None)    # sentinel

def consumer():
    while True:
        item = q.get()   # blocks if empty
        if item is None:
            break
        print(f"  Processing: {item}")
        q.task_done()

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()
```

---

## Daemon threads

```python
import threading
import time

def background_task():
    while True:
        print("  Background: working...")
        time.sleep(1)

# Daemon thread dies when main thread exits
t = threading.Thread(target=background_task, daemon=True)
t.start()

time.sleep(3)
print("Main thread done — daemon will be killed")
# No need to join() daemon threads
```

---

## Thread-local storage

```python
import threading

# Each thread gets its own copy of data
local_data = threading.local()

def worker(name):
    local_data.name = name   # unique per thread
    time.sleep(0.1)
    print(f"  Thread {threading.current_thread().name}: local_data.name = {local_data.name}")

threads = [threading.Thread(target=worker, args=(f"Worker-{i}",)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
# Each thread sees its own name — no interference
```

---

## Common threading patterns

### Thread pool with result collection

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_item(item):
    # Expensive I/O operation
    import time
    time.sleep(0.5)
    return item * 2

items = list(range(100))
results = []

with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_item = {executor.submit(process_item, item): item for item in items}
    for future in as_completed(future_to_item):
        item = future_to_item[future]
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            print(f"  Item {item} failed: {e}")

print(f"Processed {len(results)} items")
```

---

## The GIL's impact on threads

```python
import threading
import time

def cpu_bound():
    """CPU work — GIL prevents parallelism."""
    total = 0
    for i in range(10_000_000):
        total += i

# Single thread
start = time.perf_counter()
cpu_bound()
print(f"1 thread: {time.perf_counter() - start:.2f}s")   # ~0.7s

# 4 threads — NOT faster! (GIL contention)
start = time.perf_counter()
threads = [threading.Thread(target=cpu_bound) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(f"4 threads: {time.perf_counter() - start:.2f}s")   # ~2.8s (SLOWER!)

# Lesson: use multiprocessing for CPU-bound work
```

---

## Practice Exercises

1. **Build a web scraper** that downloads 50 pages concurrently with ThreadPoolExecutor (limit 10 workers).
2. **Implement a thread-safe counter** class with `increment()`, `decrement()` and `value` property.
3. **Build a producer-consumer system** with 3 producers and 5 consumers using `queue.Queue`.
4. **Demonstrate the race condition** — then fix it with a Lock, then again with an atomic operation.
5. **Implement a connection pool** using a Semaphore that limits to N simultaneous connections.
6. **Benchmark threads vs sequential** for I/O-bound and CPU-bound work — measure the difference.
