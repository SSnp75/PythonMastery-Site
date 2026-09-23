---
title: "Performance Anti-Patterns"
description: Common slow patterns in Python and the faster alternatives
---

# Performance Anti-Patterns <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisites: <a href="profiling.md">Profiling</a>, <a href="../../core/beginner/data-structures.md">Data Structures</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The most common Python slow-downs
- [x] String building the wrong way (tested)
- [x] Wrong data structure for the job (tested)
- [x] Repeated work and needless allocation
- [x] Measure before you optimize

Most Python performance problems come from a handful of recurring mistakes. Recognizing them saves you from most slow code. The comparisons here are **run-verified**.

!!! tip "Profile first"
    Don't guess where the slowness is — measure it (see [Profiling](profiling.md)). "Premature optimization is the root of all evil"; but *known* anti-patterns are worth avoiding from the start.

---

## Anti-pattern 1: string concatenation in a loop

Building a string with `+=` in a loop is **O(n²)** — each `+=` creates a whole new string (strings are immutable). Use `join` instead. Tested:

```python
n = 20000

# SLOW — O(n²): a new string built every iteration
s = ""
for i in range(n):
    s += "x"

# FAST — O(n): collect parts, join once
parts = []
for i in range(n):
    parts.append("x")
result = "".join(parts)

print(len(s), len(result))
```

Output:

```text
20000 20000
```

Both produce the same 20,000-character string, but `join` is dramatically faster at scale because it allocates once instead of `n` times. **Rule: build a list, then `"".join(list)`** — never `+=` strings in a loop.

---

## Anti-pattern 2: wrong data structure (list vs set for membership)

Checking `x in list` is **O(n)** — it scans every element. `x in set` is **O(1)**. If you test membership repeatedly, use a set. Tested:

```python
import time

data = list(range(10000))
data_set = set(data)
target = 9999

t0 = time.perf_counter()
for _ in range(1000):
    _ = target in data           # O(n) scan each time
list_time = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(1000):
    _ = target in data_set       # O(1) hash lookup
set_time = time.perf_counter() - t0

print("set faster than list:", set_time < list_time)
```

Output:

```text
set faster than list: True
```

The set is far faster for repeated membership tests. **Rule: if you check membership a lot, store it in a `set` (or `dict`), not a `list`.** Choosing the right data structure ([Data Structures](../../core/beginner/data-structures.md)) is often the single biggest performance lever.

---

## Anti-pattern 3: recomputing inside a loop

Computing the same value every iteration wastes work. Hoist invariants out:

```python
# SLOW — len(data) and the lookup recomputed every iteration
for i in range(len(data)):
    if data[i] > some_object.threshold.value:
        ...

# FAST — compute once, before the loop
n = len(data)
threshold = some_object.threshold.value
for i in range(n):
    if data[i] > threshold:
        ...
```

Attribute lookups (`some_object.threshold.value`) and function calls have real cost in Python. Pull anything constant out of the loop body.

---

## Anti-pattern 4: needless allocation & copying

Creating throwaway lists, or copying data you could iterate lazily, wastes memory and time:

```python
# SLOW — builds a full list just to sum it
total = sum([x * x for x in range(100000)])   # list comprehension allocates a list

# FAST — generator expression, no intermediate list
total = sum(x * x for x in range(100000))     # streams values, no allocation
```

Dropping the brackets (`[...]` → `(...)`) turns a list comprehension into a **generator expression** — same result, no intermediate list allocated. Use generators when you only iterate once.

---

## Anti-pattern 5: looping in Python over big numeric data

For heavy numeric work, a Python `for` loop is slow because each iteration runs interpreted bytecode. Push the loop into C — via builtins (`sum`, `map`) or, for real numeric arrays, **NumPy** (see [Vectorization](vectorization.md)):

```python
# Pure-Python loop (interpreted each step)
total = 0
for x in range(100000):
    total += x * x

# Builtin pushes iteration into C — faster
total = sum(x * x for x in range(100000))
```

Both give the same answer; the builtin version does the looping in optimized C. For large arrays, NumPy vectorization is orders of magnitude faster still.

---

## The meta-lesson

| Anti-pattern | Fix |
|---|---|
| `+=` strings in a loop | `"".join(list)` |
| `in list` repeatedly | use a `set`/`dict` |
| Recompute in loop | hoist invariants out |
| Needless list allocation | generator expressions |
| Python loop over numeric data | builtins / NumPy |

!!! warning "But measure — don't cargo-cult"
    These are *known* patterns worth avoiding, but the golden rule stands: **profile before optimizing** ([Profiling](profiling.md)). Optimizing code that isn't the bottleneck wastes effort and can hurt readability. Fix the anti-patterns in hot paths the profiler identifies.

---

## Practice exercises

1. Time string `+=` vs `join` for n = 100,000 and report the ratio.
2. Find a place in your own code testing membership on a list and switch it to a set.
3. Rewrite a loop that recomputes `len()` or an attribute each iteration to hoist it out.
4. Convert a list comprehension used only for summing into a generator expression.
5. Profile a slow function you have and identify which anti-pattern (if any) it hits.
