---
title: Asyncio
description: async/await, event loop, tasks, gather, streams, TaskGroup and async patterns
---

# Asyncio <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisite: <a href="../../core/intermediate/iterators-generators/">Generators</a></span>
  </div>
</div>

---

## How asyncio works

Asyncio uses a **single thread** with cooperative multitasking. When one coroutine awaits I/O, the event loop runs another.

```
Event Loop (single thread):
┌─────────────────────────────────────────────┐
│  Task A: running...                          │
│  Task A: await network_call()  ← suspends   │
│  Task B: running... (while A waits)          │
│  Task B: await file_read()     ← suspends   │
│  Task A: network done! resumes               │
│  Task A: complete                            │
│  Task B: file done! resumes                  │
│  Task B: complete                            │
└─────────────────────────────────────────────┘
```

---

## Coroutines and await

```python
import asyncio

async def fetch_data(url: str, delay: float) -> dict:
    """Simulate an async HTTP request."""
    print(f"  Fetching {url}...")
    await asyncio.sleep(delay)   # non-blocking sleep (simulates I/O)
    print(f"  Got response from {url}")
    return {"url": url, "data": f"Response from {url}"}

async def main():
    # Sequential — each waits for the previous (slow)
    r1 = await fetch_data("api/users", 1)
    r2 = await fetch_data("api/posts", 1)
    r3 = await fetch_data("api/comments", 1)
    # Total time: ~3 seconds

asyncio.run(main())
```

---

## Concurrent execution with gather

```python
async def main():
    # Concurrent — all run together (fast!)
    results = await asyncio.gather(
        fetch_data("api/users", 1),
        fetch_data("api/posts", 1),
        fetch_data("api/comments", 1),
    )
    # Total time: ~1 second (all started simultaneously)
    for r in results:
        print(r["url"])

asyncio.run(main())
```

---

## create_task — start now, await later

```python
async def main():
    # Start tasks immediately
    task1 = asyncio.create_task(fetch_data("api/users", 2))
    task2 = asyncio.create_task(fetch_data("api/posts", 1))

    # Do other work while tasks run
    print("  Doing other work...")
    await asyncio.sleep(0.5)

    # Now collect results
    result1 = await task1
    result2 = await task2
    print(f"  Got {result1['url']} and {result2['url']}")

asyncio.run(main())
```

---

## TaskGroup (Python 3.11+) — structured concurrency

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data("api/users", 1))
        task2 = tg.create_task(fetch_data("api/posts", 1))
        task3 = tg.create_task(fetch_data("api/comments", 1))

    # All tasks guaranteed done when we reach here
    # If any task raises — all others are cancelled
    print(task1.result(), task2.result(), task3.result())

asyncio.run(main())
```

### TaskGroup vs gather

| Feature | `gather` | `TaskGroup` |
|---|---|---|
| Error handling | Returns exceptions or raises first | Cancels all on first error |
| Structured | No | Yes (scoped lifetime) |
| Cancel behavior | Manual | Automatic |
| Python version | 3.4+ | 3.11+ |

---

## Error handling

```python
async def might_fail(name, should_fail=False):
    await asyncio.sleep(0.5)
    if should_fail:
        raise ValueError(f"{name} failed!")
    return f"{name} succeeded"

# gather with return_exceptions
async def main():
    results = await asyncio.gather(
        might_fail("A"),
        might_fail("B", should_fail=True),
        might_fail("C"),
        return_exceptions=True,   # don't crash — return exceptions
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"  Error: {r}")
        else:
            print(f"  Success: {r}")

asyncio.run(main())
# Output:
#   Success: A succeeded
#   Error: B failed!
#   Success: C succeeded
```

---

## Timeouts

```python
async def slow_operation():
    await asyncio.sleep(10)
    return "done"

async def main():
    # Timeout a single operation
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
    except asyncio.TimeoutError:
        print("  Timed out!")

    # Timeout with context manager (Python 3.11+)
    try:
        async with asyncio.timeout(2.0):
            await slow_operation()
    except TimeoutError:
        print("  Timed out!")

asyncio.run(main())
```

---

## asyncio.Queue — async producer/consumer

```python
import asyncio
import random

async def producer(queue: asyncio.Queue, name: str):
    for i in range(5):
        item = f"{name}-item-{i}"
        await asyncio.sleep(random.uniform(0.1, 0.5))
        await queue.put(item)
        print(f"  {name} produced: {item}")
    await queue.put(None)   # sentinel

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        print(f"  {name} consuming: {item}")
        await asyncio.sleep(random.uniform(0.2, 0.8))   # simulate work
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=5)

    producers = [asyncio.create_task(producer(queue, f"P{i}")) for i in range(2)]
    consumers = [asyncio.create_task(consumer(queue, f"C{i}")) for i in range(3)]

    await asyncio.gather(*producers)
    # Signal consumers to stop
    for _ in consumers:
        await queue.put(None)
    await asyncio.gather(*consumers)

asyncio.run(main())
```

---

## Semaphore — limit concurrency

```python
import asyncio
import httpx

# Limit to 10 simultaneous connections
sem = asyncio.Semaphore(10)

async def fetch_with_limit(client: httpx.AsyncClient, url: str):
    async with sem:   # at most 10 running at once
        response = await client.get(url)
        return response.status_code

async def main():
    urls = [f"https://httpbin.org/delay/1?i={i}" for i in range(50)]
    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_limit(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
    print(f"  Fetched {len(results)} URLs")

asyncio.run(main())
```

---

## Async generators

```python
async def async_range(start, stop, delay=0.1):
    """Async generator — yields values with delays."""
    for i in range(start, stop):
        await asyncio.sleep(delay)
        yield i

async def main():
    async for value in async_range(0, 10, 0.1):
        print(f"  Got: {value}")

    # Async comprehension
    values = [v async for v in async_range(0, 5)]
    print(values)   # [0, 1, 2, 3, 4]

asyncio.run(main())
```

---

## Async context managers

```python
import asyncio

class AsyncConnection:
    async def __aenter__(self):
        print("  Connecting...")
        await asyncio.sleep(0.5)
        self.connected = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("  Disconnecting...")
        await asyncio.sleep(0.2)
        self.connected = False
        return False

    async def query(self, sql: str):
        await asyncio.sleep(0.1)
        return f"Result of: {sql}"

async def main():
    async with AsyncConnection() as conn:
        result = await conn.query("SELECT * FROM users")
        print(f"  {result}")

asyncio.run(main())
```

---

## Real-world pattern: async HTTP client

```python
import asyncio
import httpx

async def fetch_all_pages(base_url: str, pages: int) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(f"{base_url}?page={p}")
            for p in range(1, pages + 1)
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses if r.status_code == 200]

async def main():
    data = await fetch_all_pages("https://api.example.com/items", 10)
    print(f"  Fetched {len(data)} pages")

asyncio.run(main())
```

---

## Running blocking code in async context

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def blocking_io():
    """Legacy blocking function."""
    import time
    time.sleep(2)
    return "done"

def cpu_heavy():
    """CPU-bound function."""
    return sum(i**2 for i in range(10_000_000))

async def main():
    loop = asyncio.get_event_loop()

    # Run blocking I/O in thread pool
    result = await loop.run_in_executor(None, blocking_io)
    print(result)

    # Run CPU work in process pool
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_heavy)
    print(result)

asyncio.run(main())
```

---

## Practice Exercises

1. **Build an async web scraper** that fetches 100 URLs concurrently with a Semaphore limit of 20.
2. **Implement async retry logic** — retry failed requests up to 3 times with exponential backoff.
3. **Build a chat server** using asyncio streams (TCP socket programming).
4. **Compare performance**: sequential vs `gather` vs `TaskGroup` for 50 HTTP requests.
5. **Implement a rate limiter** using asyncio (max N requests per second).
6. **Build an async job queue** with priority ordering and worker cancellation.
