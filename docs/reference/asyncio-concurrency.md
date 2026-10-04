---
title: "Asyncio & Concurrency — Deep Dive"
description: Coroutines, gather vs create_task, TaskGroup, synchronization primitives, timeouts, to_thread and async context managers
---

# Asyncio & Concurrency <span class="pm-badge pm-badge-proficient">Deep Dive</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../systems/proficient/asyncio/">Asyncio</a></span>
  </div>
</div>

<div class="pm-next">
<strong>✅ Related</strong>
<a href="../systems/proficient/concurrency-patterns/">Concurrency Patterns</a>
<a href="../systems/proficient/futures-executors/">Futures & Executors</a>
<a href="generators-decorators-filter.md">Generators & Streaming</a>
</div>

---

Asyncio runs many I/O-bound tasks concurrently on a **single thread** using an event loop and
cooperative multitasking. A coroutine runs until it hits `await`, then yields control so
other coroutines can progress. Every example below runs as-is.

---

## Vocabulary

*Vocabulary in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

| Term | Meaning |
|---|---|
| **Coroutine** | an `async def` function; calling it returns a coroutine object, it doesn't run yet |
| **Task** | a coroutine scheduled on the event loop, running concurrently |
| **Future** | a low-level awaitable holding a result that will arrive later |
| **Event loop** | the scheduler that resumes coroutines when their awaited work is ready |
| **Concurrency** | many tasks making progress by interleaving (one thread) |
| **Parallelism** | many tasks executing literally at once (multiple cores/threads) |

!!! note "Concurrency ≠ parallelism"
    Asyncio gives **concurrency**, not parallelism — great for I/O-bound work (network, disk)
    where tasks spend time waiting. For CPU-bound work, use processes (see
    [Multiprocessing](../systems/proficient/multiprocessing.md)).

---

## Define and run

*Define and run in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

```python
import asyncio

async def greet(name):
    await asyncio.sleep(0)      # yield control to the loop
    return f"hi {name}"

print(asyncio.run(greet("alice")))   # hi alice
```

---

## `gather` — run coroutines concurrently and collect results

*gather — run coroutines concurrently and collect results, part of Asyncio & Concurrency — Deep Dive.*

```python
import asyncio

async def work(n):
    await asyncio.sleep(0.01)
    return n * 2

async def main():
    return await asyncio.gather(work(1), work(2), work(3))

print(asyncio.run(main()))   # [2, 4, 6]  (order preserved)
```

`gather` returns results in the **order of the arguments**, not completion order.

---

## `gather` vs `create_task`

*gather vs create_task in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

Both run work concurrently. `gather` is the batch shortcut; `create_task` gives you a handle
you can await individually, cancel, or inspect.

```python
import asyncio

async def brew():
    await asyncio.sleep(0.01)
    return "coffee"

async def toast():
    await asyncio.sleep(0.01)
    return "bagel"

async def with_gather():
    a, b = await asyncio.gather(brew(), toast())
    return a, b

async def with_tasks():
    t1 = asyncio.create_task(brew())    # starts running immediately
    t2 = asyncio.create_task(toast())
    return await t1, await t2

print(asyncio.run(with_gather()))   # ('coffee', 'bagel')
print(asyncio.run(with_tasks()))    # ('coffee', 'bagel')
```

!!! tip "create_task starts work eagerly"
    `create_task` schedules the coroutine right away. If you just `await brew()` directly it
    runs to completion before the next line — that's sequential, not concurrent.

---

## `TaskGroup` — structured concurrency (3.11+)

*TaskGroup — structured concurrency, part of Asyncio & Concurrency — Deep Dive.*

`TaskGroup` is the modern, safer way to run a group of tasks: it waits for all of them, and
if any raises, it cancels the rest and propagates the error. No orphaned tasks.

```python
import asyncio

async def work(n):
    await asyncio.sleep(0.01)
    return n

async def main():
    results = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(work(i)) for i in range(3)]
    return [t.result() for t in tasks]

print(asyncio.run(main()))   # [0, 1, 2]
```

---

## Timeouts

*Timeouts in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

```python
import asyncio

async def slow():
    await asyncio.sleep(10)

async def main():
    try:
        async with asyncio.timeout(0.01):   # 3.11+
            await slow()
    except TimeoutError:
        return "timed out"

print(asyncio.run(main()))   # timed out
```

For a single awaitable, `asyncio.wait_for(coro, timeout)` does the same.

---

## Synchronization primitives

*Synchronization primitives in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

Even single-threaded, you need coordination when tasks share state or a limited resource.

### Lock — mutual exclusion

```python
import asyncio

async def main():
    lock = asyncio.Lock()
    log = []

    async def critical(n):
        async with lock:                 # only one task inside at a time
            log.append(f"enter {n}")
            await asyncio.sleep(0.01)
            log.append(f"exit {n}")

    await asyncio.gather(critical(1), critical(2))
    return log

print(asyncio.run(main()))
# ['enter 1', 'exit 1', 'enter 2', 'exit 2']  — never interleaved
```

### Semaphore — limit concurrency to N

```python
import asyncio

async def main():
    sem = asyncio.Semaphore(2)   # at most 2 at once
    active = 0
    peak = 0

    async def task():
        nonlocal active, peak
        async with sem:
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.01)
            active -= 1

    await asyncio.gather(*(task() for _ in range(6)))
    return peak

print(asyncio.run(main()))   # 2  (never more than 2 concurrent)
```

### Event — one task signals others

```python
import asyncio

async def main():
    event = asyncio.Event()
    order = []

    async def waiter():
        await event.wait()
        order.append("resumed")

    async def setter():
        await asyncio.sleep(0.01)
        order.append("set")
        event.set()

    await asyncio.gather(waiter(), setter())
    return order

print(asyncio.run(main()))   # ['set', 'resumed']
```

### Queue — producer/consumer

```python
import asyncio

async def main():
    q = asyncio.Queue()
    results = []

    async def producer():
        for i in range(3):
            await q.put(i)
        await q.put(None)   # sentinel

    async def consumer():
        while (item := await q.get()) is not None:
            results.append(item * 10)

    await asyncio.gather(producer(), consumer())
    return results

print(asyncio.run(main()))   # [0, 10, 20]
```

---

## Running blocking code without freezing the loop

*Running blocking code without freezing the loop in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

A blocking call (CPU work, a non-async library) stalls the whole event loop. Offload it to a
thread with `asyncio.to_thread`:

```python
import asyncio

def blocking_sum(n):       # ordinary blocking function
    return sum(range(n))

async def main():
    return await asyncio.to_thread(blocking_sum, 1000)

print(asyncio.run(main()))   # 499500
```

---

## Async context managers

*Async context managers in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

Resources with async setup/teardown use `async with`. Define one with
`__aenter__`/`__aexit__` or the `@asynccontextmanager` decorator:

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def connection():
    opened = []
    opened.append("open")
    try:
        yield opened
    finally:
        opened.append("close")

async def main():
    async with connection() as c:
        c.append("use")
    return c

print(asyncio.run(main()))   # ['open', 'use', 'close']
```

### Common async context managers in the ecosystem

| Category | Library / API | Manages |
|---|---|---|
| Async files | `aiofiles.open` | non-blocking file read/write |
| Network streams | `asyncio.open_connection` | reader/writer stream lifecycle |
| Locks / semaphores | `asyncio.Lock`, `Semaphore` | shared-state coordination |
| HTTP client | `aiohttp.ClientSession`, `httpx.AsyncClient` | connection pooling + cleanup |
| Databases | SQLAlchemy `AsyncSession` | connection pool + transaction |
| Message brokers | `aiokafka`, `redis.asyncio` | broker connection lifecycle |
| WebSockets | `websockets.connect` | handshake + close |
| Task groups | `asyncio.TaskGroup` (3.11+) | grouped task lifecycle |
| Timeouts | `asyncio.timeout` (3.11+) | cancel block on timeout |
| Custom | `__aenter__` / `__aexit__` | any async resource |

---

## Async iteration

*Async iteration in Asyncio & Concurrency — Deep Dive — what it is and when to use it.*

Consume an async generator with `async for`:

```python
import asyncio

async def countdown(n):
    while n > 0:
        await asyncio.sleep(0.001)
        yield n
        n -= 1

async def main():
    return [x async for x in countdown(3)]

print(asyncio.run(main()))   # [3, 2, 1]
```

---

## Practice exercises

1. Fetch three fake "URLs" concurrently with `gather` where each is an `asyncio.sleep` + return; confirm total time ≈ the longest, not the sum.
2. Use a `Semaphore(3)` to cap concurrent downloads at 3 out of 10 tasks.
3. Convert a `gather` of tasks to a `TaskGroup` and make one task raise — observe the others get cancelled.
4. Build a producer/consumer with `asyncio.Queue` and multiple consumers.
5. Wrap a blocking `time.sleep`-based function with `asyncio.to_thread` and run it alongside async work.
