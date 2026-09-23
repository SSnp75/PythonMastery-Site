---
title: "Memory Profiling"
description: Find memory leaks and reduce usage with tracemalloc and friends
---

# Memory Profiling <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisites: <a href="profiling.md">Profiling</a>, <a href="../../core/advanced/memory-model.md">Memory Model</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why memory matters (leaks, limits)
- [x] `tracemalloc` — the built-in profiler (tested)
- [x] Comparing snapshots to find growth
- [x] Finding leaks with objgraph
- [x] Reduction strategies

CPU profiling ([Profiling](profiling.md)) tells you where *time* goes; **memory profiling** tells you where *memory* goes — essential for finding leaks and fitting within limits (servers, [embedded devices](../../embedded/embedded-linux.md)). Python's built-in `tracemalloc` is **run-verified** below.

---

## Why memory matters

Even with garbage collection, Python programs can:
- **Leak** — hold references to objects that are never released, so memory grows unboundedly (a long-running server slowly consuming all RAM).
- **Bloat** — use far more memory than necessary (loading a whole file when you could stream it).
- **Hit limits** — crash with `MemoryError`, or get killed by the OS/container.

Memory profiling finds *what* is holding memory and *where* it was allocated.

---

## `tracemalloc`: the built-in tool (tested)

`tracemalloc` (standard library) tracks allocations and can compare snapshots to show what grew. Runnable:

```python
import tracemalloc

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

big = [i for i in range(100_000)]        # allocate something

snapshot2 = tracemalloc.take_snapshot()
stats = snapshot2.compare_to(snapshot1, "lineno")   # what changed?

print("largest new allocation grew:", stats[0].size_diff > 0)

current, peak = tracemalloc.get_traced_memory()
print("peak tracked memory > 0:", peak > 0)
tracemalloc.stop()
```

Output:

```text
largest new allocation grew: True
peak tracked memory > 0: True
```

`compare_to` between two snapshots shows exactly which lines allocated the most new memory — the `big` list here tops the list. `get_traced_memory()` reports current and **peak** usage. This snapshot-diff technique is the core method for hunting leaks: snapshot, run a suspected-leaky operation, snapshot again, and see what grew.

---

## The leak-hunting workflow

For a long-running process that slowly grows:

```python
import tracemalloc
tracemalloc.start()

baseline = tracemalloc.take_snapshot()
# ... run the operation you suspect leaks, many times ...
after = tracemalloc.take_snapshot()

# Show the top 10 growth sites
for stat in after.compare_to(baseline, "lineno")[:10]:
    print(stat)
```

If the same line's allocation keeps growing across iterations that *should* be steady-state, that's your leak — usually a cache/list/dict that's appended to but never cleared, or objects kept alive by a lingering reference.

---

## Other tools

| Tool | Use |
|---|---|
| **tracemalloc** | Built-in; snapshot diffs, allocation tracebacks |
| **memray** | Powerful modern allocator profiler (flame graphs); by Bloomberg |
| **objgraph** | Visualize object reference graphs — find *what* holds a leak alive |
| **sys.getsizeof** | Size of a single object (shallow) |
| **memory_profiler** | Line-by-line memory usage of a function |

```python
import sys
print(sys.getsizeof([]))        # bytes for an empty list (shallow only)
```

!!! note "External tools follow documented APIs"
    memray, objgraph, and memory_profiler aren't installed here (the `tracemalloc` and `sys.getsizeof` examples are run-verified). For serious leak hunts, **memray** (allocation flame graphs) and **objgraph** (why is this object still alive? — it draws the reference chain) are the go-to third-party tools.

---

## Reduction strategies

Once you know where memory goes, common fixes:

- **Stream, don't load.** Process a file/generator lazily instead of reading it all into memory (generators — see [Iterators & Generators](../../core/intermediate/iterators-generators.md)).
- **`__slots__`.** For classes with many instances, `__slots__` removes the per-instance `__dict__`, cutting memory substantially.
- **Right-size data structures.** `array`/NumPy for numeric data instead of lists of Python ints; `set` membership; sparse structures ([Sparse Tensors](../../scientific/sparse-tensors.md)) for mostly-zero data.
- **Release references.** Clear caches, break reference cycles, don't hold onto data you're done with.
- **`gc` tuning.** For pause-sensitive code, understand the garbage collector ([Garbage Collection](../../core/advanced/garbage-collection.md)).

```python
class Point:
    __slots__ = ("x", "y")     # no per-instance __dict__ -> less memory
    def __init__(self, x, y):
        self.x, self.y = x, y
```

---

## Practice exercises

1. Use `tracemalloc` snapshot-diff to find which of two operations allocates more.
2. Create a class with and without `__slots__`, make 100k instances of each, and compare `tracemalloc` peak.
3. Simulate a leak (a module-level list you keep appending to) and detect it via repeated snapshots.
4. Compare `sys.getsizeof` for a list of 1000 ints vs an `array('i', ...)` of the same.
5. Convert a function that reads a whole file into one that streams it line by line, and reason about the memory difference.
