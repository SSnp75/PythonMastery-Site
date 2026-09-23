---
title: "Futures & Executors"
description: Offload work to thread and process pools with concurrent.futures
---

# Futures & Executors <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prereqs: <a href="threading.md">Threading</a>, <a href="multiprocessing.md">Multiprocessing</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What a future represents
- [x] Thread vs process pools
- [x] `map` and `submit` / `as_completed` (tested)
- [x] Choosing pool type by workload
- [x] Handling results and errors

`concurrent.futures` is the standard-library's high-level interface for running work concurrently — you hand it functions, it runs them in a pool of threads or processes, and gives you **futures** (placeholders for results). It's the easiest way to parallelize. Examples here are **run-verified**.

---

## A future is a promise of a result

A **future** is an object representing a computation that may not be done yet. You get it immediately when you submit work; later you call `.result()` to get the value (blocking until ready).

```
   submit(fn) ──▶ Future (pending) ──runs in pool──▶ Future (done) ──.result()──▶ value
```

Two **executors** manage the pool:
- **`ThreadPoolExecutor`** — pool of threads. Best for **I/O-bound** work (network, disk) where the GIL is released while waiting.
- **`ProcessPoolExecutor`** — pool of processes. Best for **CPU-bound** work, sidestepping the GIL for true parallelism (see [Threading](threading.md) on the GIL).

---

## `map` — parallel over an iterable (tested)

The simplest pattern: apply a function to every item, in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

def square(x):
    return x * x

with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(square, range(6)))

print(results)
```

Output:

```text
[0, 1, 4, 9, 16, 25]
```

`ex.map` runs `square` on each input across the pool and returns results **in input order**. The `with` block cleanly shuts the pool down when done. Swap `ThreadPoolExecutor` for `ProcessPoolExecutor` and CPU-bound work runs on multiple cores.

---

## `submit` + `as_completed` — results as they finish (tested)

When you want each result the moment it's ready (not in submission order):

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def square(x):
    return x * x

with ThreadPoolExecutor(max_workers=3) as ex:
    futures = [ex.submit(square, n) for n in [2, 3, 4]]
    results = sorted(f.result() for f in as_completed(futures))

print(results)
```

Output:

```text
[4, 9, 16]
```

`submit` returns a future immediately; `as_completed` yields each future as it finishes. This is ideal when tasks take varying times and you want to process fast ones without waiting for slow ones. (`.result()` also *re-raises* any exception the task hit — so errors surface when you collect results.)

---

## Choosing the pool

| Workload | Executor | Why |
|---|---|---|
| **I/O-bound** (HTTP, files, DB) | `ThreadPoolExecutor` | Threads wait efficiently; GIL released during I/O |
| **CPU-bound** (math, parsing, compression) | `ProcessPoolExecutor` | True parallelism across cores, bypassing the GIL |

Getting this wrong is the classic mistake: threads won't speed up CPU-bound work (the GIL serializes it), and processes add overhead for I/O-bound work.

!!! tip "Start here for parallelism"
    `concurrent.futures` is usually the right first tool — higher-level and safer than managing raw threads/processes. Reach for lower-level `threading`/`multiprocessing` only when you need fine control. For async I/O at large scale, see [Asyncio](asyncio.md).

---

## Error handling

Exceptions in a task don't crash the pool — they're stored in the future and raised when you call `.result()`:

```python
from concurrent.futures import ThreadPoolExecutor

def risky(x):
    if x == 0:
        raise ValueError("cannot process zero")
    return 10 / x

with ThreadPoolExecutor() as ex:
    fut = ex.submit(risky, 0)
    try:
        fut.result()          # re-raises the ValueError here
    except ValueError as e:
        print("caught:", e)   # caught: cannot process zero
```

Always retrieve `.result()` (or check `.exception()`) so failures aren't silently swallowed.

---

## Practice exercises

1. Use `ThreadPoolExecutor` to fetch several URLs "concurrently" (simulate with `time.sleep`) and time it vs sequential.
2. Switch a CPU-bound task (e.g. summing squares to a big N) from thread to process pool and compare timing.
3. Use `as_completed` with tasks of different durations and print results in completion order.
4. Add a per-task timeout with `future.result(timeout=...)` and handle `TimeoutError`.
5. Explain why a `ThreadPoolExecutor` won't speed up a pure-Python CPU-bound loop.
