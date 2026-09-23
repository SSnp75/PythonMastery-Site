---
title: "Event Loop Internals"
description: How the asyncio event loop schedules and runs coroutines under the hood
---

# Event Loop Internals <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="asyncio.md">Asyncio</a>, <a href="../../core/intermediate/iterators-generators.md">Generators</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What an event loop actually is
- [x] Build a tiny loop from scratch (tested)
- [x] How coroutines suspend and resume
- [x] Selectors and I/O readiness
- [x] The task lifecycle

`asyncio` can feel like magic. It isn't — at its core is an **event loop**: a simple loop that pulls ready callbacks off a queue and runs them. Understanding it demystifies async Python. The mini-loop here is **run-verified**.

---

## What an event loop is

An event loop runs one thing at a time, but switches between many tasks whenever one would *wait* (for I/O, a timer, etc.). Instead of blocking, a task yields control back to the loop, which runs something else until the first task is ready to continue.

```
   loop:
     while there is work:
       take the next ready callback
       run it (it may schedule more callbacks)
   → single thread, but never idle while any task can progress
```

This is how one thread handles thousands of concurrent connections — it's never *blocked*, just juggling.

---

## A tiny event loop (tested)

The essence is a queue of ready callbacks. Runnable:

```python
from collections import deque

class MiniLoop:
    def __init__(self):
        self.ready = deque()

    def call_soon(self, fn):
        self.ready.append(fn)          # schedule a callback

    def run(self):
        out = []
        while self.ready:
            fn = self.ready.popleft()  # take the next ready callback
            fn(out)                    # run it (may schedule more)
        return out
```

```python
loop = MiniLoop()

def a_cb(out):
    out.append("a")
    loop.call_soon(lambda o: o.append("a2"))   # schedule follow-up work

def b_cb(out):
    out.append("b")

loop.call_soon(a_cb)
loop.call_soon(b_cb)
print(loop.run())
```

Output:

```text
['a', 'b', 'a2']
```

`a_cb` and `b_cb` run in FIFO order; `a_cb` schedules `a2`, which runs *after* `b` (it was appended to the back of the queue). That's the whole scheduling model in miniature — a fair, FIFO ready-queue. Real `asyncio` is this idea plus timers and I/O readiness.

---

## How coroutines suspend and resume

Real async tasks are **coroutines** (`async def`). When a coroutine hits `await` on something not ready, it **suspends** — returning control to the loop — and the loop resumes it later when the awaited thing is ready. Under the hood this uses the same mechanism as generators (see [Generators](../../core/intermediate/iterators-generators.md)): `await` is a suspension point, like `yield`.

```
   coroutine runs ──await (not ready)──▶ suspends, loop takes over
   loop runs others ──awaited thing ready──▶ resumes the coroutine where it left off
```

So a coroutine is a resumable function, and the event loop is the scheduler deciding which resumable function to advance next.

---

## Selectors: knowing when I/O is ready

The piece our mini-loop omits: how does the loop know a socket has data? It uses the OS's **I/O multiplexing** — `select`, `epoll` (Linux), `kqueue` (macOS), exposed via Python's `selectors` module. The loop asks the OS "which of these sockets are ready?" and only resumes tasks waiting on ready sockets.

```python
import selectors    # stdlib

sel = selectors.DefaultSelector()   # picks epoll/kqueue/select for your OS
# sel.register(sock, selectors.EVENT_READ, callback)
# events = sel.select(timeout)  -> only ready sockets come back
```

This is why async handles thousands of connections efficiently: instead of a thread per connection, one loop asks the OS which connections need attention and services only those.

---

## The task lifecycle

An `asyncio` task moves through states:

```
   PENDING ──scheduled──▶ RUNNING ──await──▶ SUSPENDED ──ready──▶ RUNNING ──▶ DONE
                                                                        │
                                                          (or CANCELLED / raised)
```

The loop drives this: it resumes suspended tasks when their awaited events fire, until each finishes (with a result or exception) or is cancelled.

!!! tip "You don't build event loops — you understand them"
    In practice you use `asyncio`'s loop, not a hand-rolled one. But knowing it's "just" a ready-queue + OS readiness polling makes async behavior predictable: tasks only switch at `await` points, everything runs on one thread, and a blocking (non-async) call *freezes the whole loop*. That last point is the #1 async pitfall.

---

## Practice exercises

1. Add a `call_later(delay, fn)` to `MiniLoop` using a list of (time, fn) sorted by time.
2. Show that a blocking call inside a callback stalls the whole `MiniLoop` (nothing else runs).
3. Explain, using the queue model, why `await` is a cooperative switch point but a `time.sleep` is not.
4. Read the `selectors` docs and explain what `sel.select()` returns and why it's efficient.
5. Trace the task lifecycle for a coroutine that awaits, gets resumed, then raises an exception.
