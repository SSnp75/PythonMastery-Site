---
title: "Green Threads"
description: Cooperative lightweight threads with gevent and greenlets
---

# Green Threads <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisites: <a href="asyncio.md">Asyncio</a>, <a href="event-loop-internals.md">Event Loop Internals</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What green threads are
- [x] Cooperative vs preemptive scheduling (tested demo)
- [x] gevent and monkey-patching
- [x] Green threads vs asyncio vs OS threads
- [x] When to use them

**Green threads** (also called lightweight threads or coroutines) are threads managed by a *library* rather than the OS. Thousands can run in one OS thread, switching cooperatively when one would block. The cooperative-scheduling demo here is **run-verified**.

---

## The idea

An OS thread is heavyweight (its own stack, kernel scheduling). A **green thread** is cheap — the library schedules it in user space, switching at I/O points. You can run tens of thousands, versus maybe thousands of OS threads.

The catch: green threads are **cooperative**. They only switch when a task voluntarily yields (typically at an I/O call). One task that never yields blocks all the others — unlike OS threads, which the kernel can preempt at any time.

---

## Cooperative scheduling (tested demo)

Generators let us model cooperative switching in pure Python — each task runs until it `yield`s, then the scheduler moves on:

```python
def task(name, n, log):
    for i in range(n):
        log.append(f"{name}:{i}")
        yield                       # cooperatively give up control

def run(tasks):
    log = []
    active = list(tasks)
    while active:
        nxt = []
        for t in active:
            try:
                next(t)             # advance one step
                nxt.append(t)
            except StopIteration:
                pass                # task finished
        active = nxt
    return log

log = []
run([task("A", 2, log), task("B", 3, log)])
print(log)
```

Output:

```text
['A:0', 'B:0', 'A:1', 'B:1', 'B:2']
```

The two tasks **interleave** (A:0, B:0, A:1, B:1, then B alone) because each yields after one step — round-robin cooperative scheduling. This is conceptually what a green-thread library does, except it switches automatically at I/O calls rather than explicit `yield`s.

---

## gevent and greenlets

The classic Python green-thread library is **gevent**, built on **greenlet**:

```python
import gevent                       # pip install gevent
from gevent import monkey
monkey.patch_all()                  # make stdlib blocking calls cooperative

def worker(n):
    gevent.sleep(1)                 # yields to other greenlets instead of blocking
    return n * 2

jobs = [gevent.spawn(worker, i) for i in range(1000)]
gevent.joinall(jobs)                # 1000 "threads" in one OS thread
```

!!! note "gevent snippet follows documented API"
    gevent isn't installed here (the cooperative-scheduler demo above **is** run-verified). Its trick is **monkey-patching**: `monkey.patch_all()` swaps the standard library's blocking functions (socket, time.sleep, etc.) for cooperative versions, so *existing* code becomes non-blocking without rewriting it as `async`.

!!! warning "Monkey-patching is invasive"
    `monkey.patch_all()` rewrites standard-library behavior globally at runtime. It's powerful (unmodified libraries become async-friendly) but can cause subtle bugs and conflicts. Do it once, at the very start of the program, before other imports — and understand you've changed how the whole process behaves.

---

## Green threads vs the alternatives

| | Green threads (gevent) | asyncio | OS threads |
|---|---|---|---|
| Scheduling | Cooperative (implicit yield) | Cooperative (explicit `await`) | Preemptive (OS) |
| Syntax | Looks like normal blocking code | `async`/`await` | Normal code |
| Count feasible | Tens of thousands | Tens of thousands | Thousands |
| Explicitness | Hidden switch points | Visible `await` points | N/A |

The key contrast with **asyncio**: gevent hides the switch points (code *looks* synchronous), while asyncio makes them explicit with `await`. Modern Python has largely standardized on **asyncio** for new code because explicit `await` makes concurrency easier to reason about — but gevent remains useful for making large existing synchronous codebases concurrent without a rewrite.

---

## When to use them

- **gevent/green threads** — you have a big synchronous (I/O-bound) codebase and want concurrency without rewriting it to async. Or you're on a framework built around it.
- **asyncio** ([Asyncio](asyncio.md)) — new I/O-bound code where explicit, readable concurrency is preferred. The modern default.
- **OS threads / futures** ([Futures & Executors](futures-executors.md)) — when you need preemption or are integrating with blocking code you can't patch.

---

## Practice exercises

1. Extend the cooperative scheduler so tasks can yield a value that the scheduler collects.
2. Add a task that never yields and show it starves the others (the cooperative pitfall).
3. Explain what `monkey.patch_all()` does and why it must run before other imports.
4. Compare the green-thread demo's interleaving to how asyncio would schedule the same tasks.
5. Decide, for a legacy synchronous web scraper, whether gevent or an asyncio rewrite fits better, and why.
