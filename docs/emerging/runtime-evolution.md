---
title: "Python Runtime Evolution"
description: How CPython is changing — the GIL, free-threading, subinterpreters and faster CPython
---

# Python Runtime Evolution <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🚀 Emerging & Evolving Python</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../core/advanced/cpython-internals/">CPython Internals</a>, <a href="../systems/proficient/threading/">Threading</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What the GIL is and why it's being removed
- [x] Free-threaded Python (PEP 703)
- [x] Subinterpreters (PEP 734)
- [x] The Faster CPython project
- [x] What these mean for your code

The runtime — CPython itself — is undergoing the most significant changes in its history. Understanding them tells you where Python performance and concurrency are heading.

---

## The GIL and why it's changing

The **Global Interpreter Lock (GIL)** is a mutex that lets only *one* thread execute Python bytecode at a time, even on a multi-core CPU. It has simplified CPython's memory management for decades, but it means threads can't run Python code truly in parallel — the reason CPU-bound work uses `multiprocessing` instead of `threading` (see [Threading](../systems/proficient/threading.md)).

```
   With the GIL:                    Free-threaded (no GIL):
   core 1: [thread A]▓▓▓▓▓▓          core 1: [thread A]▓▓▓▓▓▓
   core 2:          (idle)          core 2: [thread B]▓▓▓▓▓▓
   only one runs Python at a time    both run Python in parallel
```

## Free-threaded Python (PEP 703)

The biggest change: an official, experimental **free-threaded build** of CPython (3.13+) that **removes the GIL**, letting threads run Python code on multiple cores simultaneously. This has been in the works for years and is being introduced gradually as an opt-in build so the ecosystem can adapt.

**Why it's hard:** the GIL protected reference counting and internal state. Removing it safely required rethinking object memory management throughout the interpreter — one of the most invasive changes ever made to CPython (see [Interpreter Forking](../research/interpreter-forking.md) for the fork history).

**What it means for you (eventually):** CPU-bound multithreaded Python could become genuinely parallel — no `multiprocessing` overhead. But it's **experimental**, some C extensions need updates to be compatible, and single-threaded code may be slightly slower in the free-threaded build for now. Don't rewrite your code for it yet; do watch it.

---

## Subinterpreters (PEP 734)

Another path to parallelism: **multiple independent interpreters in one process**, each with its own state (and, in newer versions, its own GIL). This gives isolation like `multiprocessing` but with lower overhead since it stays in one process.

```python
# The documented API (interpreters module, evolving)
import interpreters                 # exact import path is stabilizing

interp = interpreters.create()
interp.exec("print('hello from a subinterpreter')")
```

!!! note "Subinterpreter API is still stabilizing"
    The `interpreters` module and its exact API are new and evolving across 3.12–3.13+, so this follows the documented direction rather than being pinned/run-verified here. The concept: isolated interpreters that can run in parallel, communicating through explicit channels rather than shared memory.

Subinterpreters and free-threading are complementary approaches to the same goal — real parallelism in Python.

---

## Faster CPython

Separately from concurrency, the **Faster CPython** project (backed by Microsoft, led partly by Guido van Rossum) has been making the interpreter itself faster with **no code changes required**:

- **3.11** brought ~10-60% speedups via a "specializing adaptive interpreter" — the interpreter observes what your code does and optimizes hot paths (specializing, say, `+` for integers).
- Later versions continue this, including work toward a **JIT compiler** in CPython.

The beautiful part: you get these gains just by upgrading Python. Code that ran on 3.10 runs measurably faster on 3.12+ untouched.

```python
# Nothing special — this just runs faster on newer CPython
def hot_loop(n):
    total = 0
    for i in range(n):
        total += i * i
    return total
```

---

## What this means for your code

| Change | Do now | Watch for |
|---|---|---|
| Free-threading | Nothing — keep using multiprocessing for CPU parallelism | When it's stable + your C-ext deps support it, threads for CPU work |
| Subinterpreters | Nothing — API still settling | A lighter alternative to multiprocessing |
| Faster CPython | **Upgrade Python** — free speed | Continued gains, eventual JIT |

!!! tip "The one action to take today"
    Keep your Python version current. Faster CPython means each upgrade makes your existing code quicker for free — the lowest-effort performance win available.

---

## Practice exercises

1. Explain, in terms of the GIL, why `threading` doesn't speed up a CPU-bound loop today but `multiprocessing` does.
2. Read PEP 703's motivation section and summarize the compatibility concern with C extensions.
3. Benchmark the same numeric loop on two Python versions you have and note any speed difference.
4. Describe how subinterpreters differ from both threads and separate processes.
5. Explain why removing the GIL was so invasive, referencing reference counting.
