---
title: Multiprocessing
description: Processes, Pool, Queue, shared memory, ProcessPoolExecutor and true parallelism
---

# Multiprocessing <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="threading/">Threading</a></span>
  </div>
</div>

---

## Why multiprocessing?

Each process has its own Python interpreter and GIL — true parallelism for CPU-bound work.

```python
import multiprocessing as mp
import time

def cpu_heavy(n):
    """CPU-bound: sum of squares."""
    return sum(i**2 for i in range(n))

# Sequential
start = time.perf_counter()
results = [cpu_heavy(5_000_000) for _ in range(4)]
print(f"Sequential: {time.perf_counter() - start:.2f}s")  # ~4s

# Parallel with Pool
start = time.perf_counter()
with mp.Pool(processes=4) as pool:
    results = pool.map(cpu_heavy, [5_000_000] * 4)
print(f"Parallel:   {time.perf_counter() - start:.2f}s")  # ~1.2s (near-linear speedup!)
```

---

## ProcessPoolExecutor (high-level API)

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_chunk(data):
    """Expensive computation on a data chunk."""
    return sum(x**2 for x in data)

# Split work across processes
chunks = [list(range(i*250000, (i+1)*250000)) for i in range(16)]

with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
    futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
    total = sum(f.result() for f in as_completed(futures))
    print(f"Total: {total}")
```

---

## Pool methods

```python
import multiprocessing as mp

def square(x):
    return x ** 2

def init_worker():
    """Called once per worker process at startup."""
    print(f"  Worker {mp.current_process().name} initialized")

with mp.Pool(processes=4, initializer=init_worker) as pool:
    # map — ordered results, blocks until all done
    results = pool.map(square, range(20))
    print(results)  # [0, 1, 4, 9, 16, ...]

    # map with chunksize (better for many small tasks)
    results = pool.map(square, range(10000), chunksize=100)

    # imap — lazy iterator (memory efficient for large inputs)
    for result in pool.imap(square, range(1000)):
        pass   # process one at a time

    # imap_unordered — fastest, results come as they finish
    for result in pool.imap_unordered(square, range(1000)):
        pass

    # starmap — for functions with multiple arguments
    args = [(2, 3), (4, 5), (6, 7)]
    results = pool.starmap(pow, args)  # [8, 1024, 279936]

    # apply_async — submit single task, get future
    future = pool.apply_async(square, (42,))
    print(future.get(timeout=5))   # 1764
```

---

## Inter-process communication

### Queue

```python
import multiprocessing as mp
import time

def producer(q):
    for i in range(10):
        q.put(f"item-{i}")
        time.sleep(0.1)
    q.put("DONE")   # sentinel

def consumer(q):
    while True:
        item = q.get()   # blocks until available
        if item == "DONE":
            break
        print(f"  Consumed: {item}")

q = mp.Queue()
p = mp.Process(target=producer, args=(q,))
c = mp.Process(target=consumer, args=(q,))
p.start(); c.start()
p.join(); c.join()
```

### Pipe (faster for 2 processes)

```python
import multiprocessing as mp

def sender(conn):
    conn.send({"type": "data", "value": 42})
    conn.send({"type": "done"})
    conn.close()

def receiver(conn):
    while True:
        msg = conn.recv()
        if msg["type"] == "done":
            break
        print(f"  Received: {msg}")
    conn.close()

parent_conn, child_conn = mp.Pipe()
p1 = mp.Process(target=sender, args=(child_conn,))
p2 = mp.Process(target=receiver, args=(parent_conn,))
p1.start(); p2.start()
p1.join(); p2.join()
```

---

## Shared memory

```python
import multiprocessing as mp
import numpy as np
from multiprocessing import shared_memory

# Create shared memory block
data = np.arange(1_000_000, dtype=np.float64)
shm = shared_memory.SharedMemory(create=True, size=data.nbytes)

# Create numpy array backed by shared memory
shared_array = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
shared_array[:] = data[:]   # copy data in

def worker(shm_name, shape, dtype):
    """Worker process — attaches to existing shared memory."""
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    arr = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    # Modify in place — visible to all processes!
    arr *= 2
    existing_shm.close()

p = mp.Process(target=worker, args=(shm.name, data.shape, data.dtype))
p.start()
p.join()

print(shared_array[:5])   # [0, 2, 4, 6, 8] — doubled by worker!

# Cleanup
shm.close()
shm.unlink()
```

### Value and Array (simpler shared state)

```python
import multiprocessing as mp

def increment(shared_counter, lock):
    for _ in range(100_000):
        with lock:
            shared_counter.value += 1

counter = mp.Value('i', 0)   # shared integer
lock = mp.Lock()

processes = [mp.Process(target=increment, args=(counter, lock)) for _ in range(4)]
for p in processes: p.start()
for p in processes: p.join()

print(f"Counter: {counter.value}")   # 400,000
```

---

## Pickling limitations

!!! warning "Objects must be picklable"
    Multiprocessing serializes objects with `pickle` to send between processes. These **cannot** be pickled:
    
    - Lambda functions
    - Nested functions (closures)
    - Open file handles
    - Database connections
    - Generators
    
    Use module-level functions or classes instead.

```python
# BAD — lambda can't be pickled
# pool.map(lambda x: x**2, range(10))   # PicklingError!

# GOOD — module-level function
def square(x):
    return x**2

pool.map(square, range(10))   # works
```

---

## Process lifecycle and error handling

```python
import multiprocessing as mp

def might_fail(x):
    if x == 3:
        raise ValueError(f"Don't like {x}!")
    return x * 2

with mp.Pool(4) as pool:
    # apply_async gives access to exceptions
    futures = [pool.apply_async(might_fail, (i,)) for i in range(5)]

    for i, future in enumerate(futures):
        try:
            result = future.get(timeout=5)
            print(f"  Task {i}: {result}")
        except ValueError as e:
            print(f"  Task {i} FAILED: {e}")
        except mp.TimeoutError:
            print(f"  Task {i} TIMED OUT")
```

---

## When to use what

| Need | Solution |
|---|---|
| I/O-bound parallelism | `threading` or `asyncio` |
| CPU-bound parallelism | `multiprocessing` |
| Simple parallel map | `ProcessPoolExecutor.map()` |
| Communication between workers | `mp.Queue` or `mp.Pipe` |
| Shared large arrays | `shared_memory` + numpy |
| Shared simple values | `mp.Value` / `mp.Array` with Lock |

---

## Practice Exercises

1. **Benchmark multiprocessing** — compare Pool with 1, 2, 4, 8 workers on a CPU-bound task.
2. **Build a parallel image processor** that resizes 100 images using Pool.
3. **Implement MapReduce** — use multiprocessing to parallelize word count across files.
4. **Use shared memory** with numpy to parallelize matrix computation across workers.
5. **Build a worker pipeline** — Process A produces → Queue → Process B transforms → Queue → Process C saves.
6. **Handle errors gracefully** — track which tasks failed and retry them.
