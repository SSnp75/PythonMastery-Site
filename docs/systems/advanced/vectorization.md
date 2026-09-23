---
title: "Vectorization"
description: Replace Python loops with array operations for massive speedups
---

# Vectorization <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../../data/intermediate/numpy.md">NumPy</a>, <a href="performance-antipatterns.md">Performance Anti-Patterns</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What vectorization is and why it's fast
- [x] The pure-Python analog (tested)
- [x] NumPy vectorized operations
- [x] Broadcasting
- [x] When it does and doesn't help

**Vectorization** means replacing explicit Python loops with array operations that run in optimized C. For numeric work it's often 10-100× faster — the single biggest performance win in scientific Python. The pure-Python analog here is **run-verified**; NumPy examples follow its documented API.

---

## Why loops are slow, arrays are fast

A Python `for` loop over numbers pays the interpreter's overhead *every iteration*: bytecode dispatch, boxing each `int` as an object, type checks. A vectorized operation hands the whole array to C code that does the loop in tight machine code with SIMD instructions — no per-element Python overhead.

```
   Python loop:   [interp] [interp] [interp] ...   (overhead × n)
   Vectorized:    [────── one C call over all n ──────]   (overhead × 1)
```

## The pure-Python analog (tested)

Even without NumPy, the *principle* — push the loop into C — shows up with builtins:

```python
data = range(100_000)

# Explicit Python loop — interpreter overhead each step
total1 = 0
for x in data:
    total1 += x * x

# Builtin sum over a generator — the loop runs in C
total2 = sum(x * x for x in data)

print(total1 == total2)
```

Output:

```text
True
```

Same result, but `sum(...)` does the iteration in C rather than interpreted Python. This is the *idea* of vectorization in miniature: move the repeated work out of the Python interpreter. NumPy takes it much further by also storing data in contiguous typed arrays and using SIMD.

---

## NumPy vectorized operations

The real thing operates on whole arrays at once:

```python
import numpy as np                 # pip install numpy

a = np.arange(1_000_000)

# Vectorized: no Python loop, runs in C
squares = a ** 2                   # square every element
total = np.sum(a * a)              # sum of squares
mask = a[a > 500]                  # select elements > 500
normalized = (a - a.mean()) / a.std()   # whole-array math
```

!!! note "NumPy snippets follow documented API"
    NumPy isn't installed here (the pure-Python `sum` example is run-verified). Each operation above replaces a Python loop with a single C-level operation over the whole array — often 50-100× faster for large arrays. This is why data science uses NumPy/Pandas instead of raw loops. See [NumPy](../../data/intermediate/numpy.md) and [BLAS & LAPACK](../../scientific/blas-lapack.md).

---

## Broadcasting

**Broadcasting** lets NumPy combine arrays of different shapes without writing loops — it "stretches" smaller arrays to match:

```python
import numpy as np

matrix = np.ones((3, 4))           # 3×4
row = np.array([1, 2, 3, 4])       # shape (4,)
result = matrix + row              # row added to EVERY row — no loop
```

Broadcasting expresses operations like "subtract the column mean from every row" as one expression, staying vectorized (and fast). It's one of NumPy's most powerful features once you internalize the rules.

---

## When vectorization helps (and doesn't)

**Helps enormously:**
- Numeric arrays with element-wise math (arithmetic, comparisons, aggregations).
- Large data where per-element Python overhead dominates.

**Doesn't help (or can't apply):**
- Non-numeric or irregular data (strings, nested structures) — arrays want homogeneous numeric types.
- Genuinely sequential algorithms where each step depends on the previous (some can be reformulated, some can't).
- Tiny data — the overhead of setting up arrays isn't worth it for a handful of values.

!!! tip "The golden rule of NumPy performance"
    **If you're writing a `for` loop over a NumPy array, you're probably doing it wrong.** Look for the vectorized expression instead. When you truly can't vectorize, options are Numba (JIT — see the Numba topic), Cython, or accepting the loop. But reach for vectorization first.

---

## Practice exercises

1. Rewrite a Python loop that computes element-wise `a[i]*b[i]` as a NumPy vectorized `a * b`.
2. Use broadcasting to subtract a per-column mean from a 2D array without any loop.
3. Time (conceptually or with NumPy installed) a 1M-element sum-of-squares: Python loop vs `np.sum(a*a)`.
4. Find a masking operation ("keep elements > threshold") and express it with boolean indexing.
5. Describe a computation that *cannot* be easily vectorized and explain why.
