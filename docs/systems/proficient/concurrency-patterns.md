---
title: Concurrency Patterns
description: Producer-consumer, fan-out/fan-in, pipeline, backpressure and actor model
---

# Concurrency Patterns <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="threading/">Threading</a>, <a href="asyncio/">Asyncio</a></span>
  </div>
</div>

---

## Pattern 1: Producer-Consumer

Multiple producers generate work, multiple consumers process it.

```python
import asyncio
import random

async def producer(queue: asyncio.Queue, name: str, count: int):
    for i in range(count):
        task = {"id": f"{name}-{i}", "data": random.randint(1, 100)}
        await queue.put(task)
        await asyncio.sleep(random.uniform(0.01, 0.1))
    print(f"  {name}: done producing")

async def consumer(queue: asyncio.Queue, name: str):
    processed = 0
    while True:
        task = await queue.get()
        if task is None:
            break
        # Simulate processing
        await asyncio.sleep(random.uniform(0.05, 0.2))
        processed += 1
        queue.task_done()
    print(f"  {name}: processed {processed} tasks")

async def main():
    queue = asyncio.Queue(maxsize=20)   # backpressure: producers wait if full

    # Start producers and consumers
    producers = [asyncio.create_task(producer(queue, f"P{i}", 50)) for i in range(3)]
    consumers = [asyncio.create_task(consumer(queue, f"C{i}")) for i in range(5)]

    # Wait for all production to finish
    await asyncio.gather(*producers)

    # Wait for queue to be fully processed
    await queue.join()

    # Stop consumers
    for _ in consumers:
        await queue.put(None)
    await asyncio.gather(*consumers)

asyncio.run(main())
```

---

## Pattern 2: Fan-out / Fan-in

Distribute work across workers, collect results.

```python
import asyncio

async def fan_out_fan_in(items: list, worker_count: int, process_fn):
    """Distribute items across N workers, collect all results."""
    queue = asyncio.Queue()
    results = []
    results_lock = asyncio.Lock()

    async def worker():
        while True:
            item = await queue.get()
            if item is None:
                break
            result = await process_fn(item)
            async with results_lock:
                results.append(result)
            queue.task_done()

    # Start workers
    workers = [asyncio.create_task(worker()) for _ in range(worker_count)]

    # Feed items
    for item in items:
        await queue.put(item)

    # Wait for all items processed
    await queue.join()

    # Stop workers
    for _ in workers:
        await queue.put(None)
    await asyncio.gather(*workers)

    return results

# Usage
async def process_item(item):
    await asyncio.sleep(0.1)
    return item * 2

async def main():
    items = list(range(100))
    results = await fan_out_fan_in(items, worker_count=10, process_fn=process_item)
    print(f"  Processed {len(results)} items, sum={sum(results)}")

asyncio.run(main())
```

---

## Pattern 3: Pipeline (staged processing)

Each stage processes and passes to the next — like Unix pipes.

```python
import asyncio

async def stage_read(output: asyncio.Queue):
    """Stage 1: read raw data."""
    for i in range(100):
        await output.put({"raw": f"record-{i}", "value": i})
    await output.put(None)

async def stage_transform(input_q: asyncio.Queue, output: asyncio.Queue):
    """Stage 2: transform data."""
    while True:
        item = await input_q.get()
        if item is None:
            await output.put(None)
            break
        item["transformed"] = item["value"] ** 2
        await output.put(item)

async def stage_filter(input_q: asyncio.Queue, output: asyncio.Queue):
    """Stage 3: filter data."""
    while True:
        item = await input_q.get()
        if item is None:
            await output.put(None)
            break
        if item["transformed"] > 100:
            await output.put(item)

async def stage_write(input_q: asyncio.Queue):
    """Stage 4: write results."""
    count = 0
    while True:
        item = await input_q.get()
        if item is None:
            break
        count += 1
    print(f"  Wrote {count} records")

async def main():
    q1 = asyncio.Queue(maxsize=10)
    q2 = asyncio.Queue(maxsize=10)
    q3 = asyncio.Queue(maxsize=10)

    await asyncio.gather(
        stage_read(q1),
        stage_transform(q1, q2),
        stage_filter(q2, q3),
        stage_write(q3),
    )

asyncio.run(main())
```

---

## Pattern 4: Backpressure

Prevent fast producers from overwhelming slow consumers:

```python
import asyncio

async def fast_producer(queue: asyncio.Queue):
    for i in range(1000):
        await queue.put(i)   # BLOCKS when queue is full!
        # This is backpressure — producer slows down automatically
    await queue.put(None)

async def slow_consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        await asyncio.sleep(0.01)   # slow processing
        queue.task_done()

async def main():
    # maxsize=10 creates backpressure
    queue = asyncio.Queue(maxsize=10)
    await asyncio.gather(
        fast_producer(queue),
        slow_consumer(queue),
    )

asyncio.run(main())
```

---

## Pattern 5: Throttle / Rate limiter

```python
import asyncio
import time

class AsyncThrottle:
    """Allow at most `rate` operations per second."""

    def __init__(self, rate: int):
        self.rate = rate
        self.semaphore = asyncio.Semaphore(rate)
        self._task = None

    async def __aenter__(self):
        await self.semaphore.acquire()
        return self

    async def __aexit__(self, *args):
        # Release after 1 second
        asyncio.get_event_loop().call_later(1.0, self.semaphore.release)

# Usage: max 5 requests per second
throttle = AsyncThrottle(rate=5)

async def limited_request(url):
    async with throttle:
        # This will naturally limit to 5/sec
        return await fetch(url)
```

---

## Pattern 6: Circuit Breaker (async version)

```python
import asyncio
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class AsyncCircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = State.CLOSED
        self.failures = 0
        self.last_failure = 0

    async def call(self, coro):
        if self.state == State.OPEN:
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = State.HALF_OPEN
            else:
                raise Exception("Circuit is OPEN — call rejected")

        try:
            result = await coro
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self):
        self.failures = 0
        self.state = State.CLOSED

    def _on_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.failure_threshold:
            self.state = State.OPEN
```

---

## Choosing the right pattern

| Scenario | Pattern |
|---|---|
| Many tasks, shared queue | Producer-Consumer |
| Distribute + collect | Fan-out / Fan-in |
| Sequential stages | Pipeline |
| Fast producer, slow consumer | Backpressure (bounded queue) |
| Rate-limited external API | Throttle / Semaphore |
| Unreliable external service | Circuit Breaker |
| Independent actors | Actor Model (use `aiochan` or manual) |

---

## Practice Exercises

1. **Build a 3-stage pipeline** that reads URLs → fetches HTML → extracts titles, with bounded queues.
2. **Implement fan-out** — distribute 1000 items across 20 workers, collect results in order.
3. **Add backpressure** to a producer-consumer system and measure throughput.
4. **Build an async rate limiter** that enforces "max 100 requests per minute".
5. **Implement the actor model** — each actor has a mailbox (Queue) and processes messages sequentially.
6. **Combine patterns** — build a web crawler with throttling, circuit breaking and pipeline stages.
