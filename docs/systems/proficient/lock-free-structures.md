---
title: "Lock-free Structures"
description: Concurrency without locks — atomics, compare-and-swap and the Python reality
---

# Lock-free Structures <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="threading.md">Threading</a>, <a href="concurrency-patterns.md">Concurrency Patterns</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What "lock-free" means
- [x] Compare-and-swap, the core primitive (tested model)
- [x] Why the GIL changes the Python picture
- [x] The practical Python approach (queue.Queue)
- [x] When lock-free actually matters

**Lock-free** data structures let multiple threads operate on shared data **without locks**, using atomic hardware instructions instead. They avoid lock problems (deadlock, priority inversion, contention) but are notoriously hard to get right. The CAS model here is **run-verified** (single-threaded, illustrating the primitive).

---

## What "lock-free" means

A normal thread-safe counter uses a lock: acquire, increment, release. If a thread holds the lock and stalls, others wait. **Lock-free** algorithms guarantee that *some* thread always makes progress, using atomic operations that either fully succeed or fully fail — no in-between state to protect.

The foundational primitive is **compare-and-swap (CAS)**: atomically, "if this memory still holds the value I expect, replace it; otherwise tell me it changed." Hardware provides this as a single uninterruptible instruction.

---

## Compare-and-swap (tested model)

Here's the *logic* of CAS (single-threaded, to show the semantics — real CAS is one atomic CPU instruction):

```python
def compare_and_swap(cell, expected, new):
    """If cell holds `expected`, set it to `new` and return True; else False."""
    if cell["v"] == expected:
        cell["v"] = new
        return True
    return False

cell = {"v": 0}
print(compare_and_swap(cell, 0, 5))    # expected 0, matches -> swap to 5
print(cell["v"])
print(compare_and_swap(cell, 0, 9))    # expected 0, but it's 5 now -> fail
print(cell["v"])
```

Output:

```text
True
5
False
5
```

The first CAS succeeds (cell was 0, becomes 5). The second **fails** because the cell no longer holds the expected 0 — so it doesn't clobber the value. Lock-free algorithms build on this: read a value, compute a new one, and CAS it in *only if nobody else changed it meanwhile*; if the CAS fails, retry. That "read-modify-CAS-retry" loop is the heart of lock-free programming.

!!! warning "Real CAS is atomic; this model is not"
    The function above is single-threaded illustration. True CAS is a single hardware instruction that can't be interrupted between the compare and the swap — that atomicity is the whole point. You cannot build a correct lock-free structure from the Python-level pseudo-CAS above, because Python code isn't atomic at that granularity.

---

## The Python reality: the GIL

Here's the crucial Python-specific truth: because of the **GIL** (see [Threading](threading.md)), only one thread executes Python bytecode at a time. This means:

- Many single-bytecode operations are *effectively* atomic already (though relying on which ones is fragile and version-dependent).
- You **cannot** implement true lock-free structures in pure Python — you don't have real atomic CAS at the Python level, and the GIL means the fine-grained parallelism lock-free algorithms exploit isn't there anyway.
- Genuine lock-free code in the Python world lives in **C extensions** (or in the interpreter itself), where real atomics are available.

The free-threaded (no-GIL) Python effort (see [Runtime Evolution](../../emerging/runtime-evolution.md)) makes this more relevant for the future, but today it's mostly a C-extension concern.

---

## The practical Python approach

For thread-safe data sharing in Python, **don't** hand-roll lock-free structures. Use the standard library's already-correct tools:

```python
import queue

q = queue.Queue()      # thread-safe FIFO — internally synchronized
q.put(1)
q.put(2)
print(q.get())         # 1  — safe across threads, no manual locking
```

`queue.Queue` (and `LifoQueue`, `PriorityQueue`) are thread-safe and battle-tested — the idiomatic way to pass data between threads (as the [Actor Model](actor-model.md) and producer-consumer patterns do). For counters/flags, a simple `threading.Lock` is clearer and fast enough given the GIL.

!!! tip "Almost never roll your own lock-free code"
    Lock-free algorithms are among the hardest code to write correctly — subtle memory-ordering bugs, the ABA problem, and races that appear only under rare timing. In Python specifically, the GIL removes most of the *need*. Use `queue.Queue`, locks, or the actor model. Reserve real lock-free work for C extensions written by people who do it full-time.

---

## When it actually matters

Lock-free techniques are genuinely important in:

- **High-performance C/C++/Rust systems** — databases, game engines, kernels.
- **CPython internals** — the interpreter uses atomics for reference counting (and much more in the no-GIL work).
- **Rust extensions** ([Rust Extensions](../advanced/rust-extensions.md)) — where you *do* have real atomics and might implement lock-free structures callable from Python.

For everyday Python, the lesson is understanding *why* you rarely need it — not implementing it.

---

## Practice exercises

1. Write the "read-modify-CAS-retry" loop in pseudocode for incrementing a counter lock-free.
2. Explain the ABA problem: why a value returning to its original can fool naive CAS.
3. Demonstrate `queue.Queue` passing data safely between two threads.
4. Explain, using the GIL, why a pure-Python lock-free structure gains you nothing today.
5. Describe how the no-GIL Python effort could change this, and where real atomics live now.
