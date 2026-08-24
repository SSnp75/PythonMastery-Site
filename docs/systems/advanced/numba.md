---
title: Numba
description: JIT compilation for numerical Python with @njit, vectorize, CUDA and parallel
---

# Numba <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../../data/intermediate/numpy/">NumPy</a>, <a href="profiling/">Profiling</a></span>
  </div>
</div>

---

## What is Numba?

Numba is a **JIT compiler** that translates Python/NumPy code to fast machine code using LLVM. Zero setup — just add a decorator.

```python
from numba import njit
import numpy as np

@njit   # compile to machine code on first call
def sum_squares(arr):
    total = 0.0
    for i in range(len(arr)):
        total += arr[i] ** 2
    return total

data = np.random.randn(10_000_000)

# First call — compiles (slow)
result = sum_squares(data)

# Subsequent calls — fast (compiled machine code)
result = sum_squares(data)   # ~100x faster than pure Python loop
```

---

## @njit vs @jit

```python
from numba import jit, njit

# @jit — falls back to Python if it can't compile (object mode)
@jit
def flexible(x):
    return x   # works with any type, but may not be fast

# @njit — strict mode, fails if it can't compile (nopython mode)
@njit   # same as @jit(nopython=True)
def strict(x):
    return x ** 2   # must use supported types/operations

# Always prefer @njit — it guarantees compiled code
```

---

## Supported operations

Numba supports:
- All numeric types (int, float, complex)
- NumPy arrays and most NumPy functions
- Loops, conditionals, functions
- Tuples (fixed-size)
- Basic math operations

Numba does NOT support:
- Dicts, sets, classes (partial support for typed versions)
- String operations
- Most of the standard library
- I/O (file, network)

---

## Parallel execution with `parallel=True`

```python
from numba import njit, prange
import numpy as np

@njit(parallel=True)
def parallel_sum(arr):
    total = 0.0
    for i in prange(len(arr)):   # prange = parallel range
        total += arr[i] ** 2
    return total

@njit(parallel=True)
def parallel_matrix_multiply(A, B):
    """Manual matrix multiply with parallelism."""
    m, k = A.shape
    k2, n = B.shape
    C = np.zeros((m, n))
    for i in prange(m):
        for j in range(n):
            total = 0.0
            for p in range(k):
                total += A[i, p] * B[p, j]
            C[i, j] = total
    return C

A = np.random.randn(1000, 1000)
B = np.random.randn(1000, 1000)
C = parallel_matrix_multiply(A, B)   # uses all CPU cores
```

---

## @vectorize — create NumPy ufuncs

```python
from numba import vectorize, float64, int64
import numpy as np

@vectorize([float64(float64, float64)])
def custom_add(x, y):
    """Element-wise custom function — works on arrays automatically."""
    if x > y:
        return x + y
    else:
        return x - y

a = np.array([1.0, 5.0, 3.0])
b = np.array([2.0, 3.0, 4.0])
print(custom_add(a, b))   # [-1.0, 8.0, -1.0]

# Works with broadcasting too!
print(custom_add(a, 2.0))  # [-1.0, 7.0, 1.0]
```

---

## @guvectorize — generalized ufuncs

```python
from numba import guvectorize, float64
import numpy as np

@guvectorize([(float64[:], float64[:])], "(n)->()")
def row_sum(row, result):
    """Sum each row of a 2D array."""
    total = 0.0
    for i in range(row.shape[0]):
        total += row[i]
    result[0] = total

matrix = np.arange(12.0).reshape(3, 4)
print(row_sum(matrix))   # [6., 22., 38.]
```

---

## CUDA kernels (GPU programming)

```python
from numba import cuda
import numpy as np
import math

@cuda.jit
def vector_add_kernel(a, b, result):
    """GPU kernel — runs on each thread."""
    idx = cuda.grid(1)   # global thread index
    if idx < a.size:
        result[idx] = a[idx] + b[idx]

# Setup
n = 1_000_000
a = np.random.randn(n).astype(np.float32)
b = np.random.randn(n).astype(np.float32)
result = np.zeros(n, dtype=np.float32)

# Copy to GPU
d_a = cuda.to_device(a)
d_b = cuda.to_device(b)
d_result = cuda.to_device(result)

# Launch kernel
threads_per_block = 256
blocks_per_grid = math.ceil(n / threads_per_block)
vector_add_kernel[blocks_per_grid, threads_per_block](d_a, d_b, d_result)

# Copy result back
result = d_result.copy_to_host()
print(np.allclose(result, a + b))   # True
```

---

## Caching — avoid recompilation

```python
@njit(cache=True)   # save compiled code to disk
def expensive_to_compile(x):
    return x ** 2 + x * 3 - 1

# First run: compiles and saves to __pycache__
# Subsequent runs: loads from cache (instant startup)
```

---

## Type signatures (ahead-of-time)

```python
from numba import njit, int64, float64

# Explicit signature — compiled immediately, not on first call
@njit(float64(float64[:]))
def array_sum(arr):
    total = 0.0
    for i in range(len(arr)):
        total += arr[i]
    return total

# Multiple signatures
@njit([
    float64(float64[:]),
    int64(int64[:]),
])
def generic_sum(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
```

---

## Debugging Numba code

```python
from numba import njit

# Inspect generated LLVM IR
@njit
def simple(x, y):
    return x + y

simple(1, 2)   # trigger compilation
print(simple.inspect_llvm())   # LLVM IR
print(simple.inspect_asm())    # assembly

# Check compilation succeeded
print(simple.signatures)   # [(int64, int64) -> int64]

# Performance warning
from numba import NumbaPendingDeprecationWarning
import warnings
warnings.simplefilter("always", NumbaPendingDeprecationWarning)
```

---

## When to use Numba vs alternatives

| Scenario | Best choice |
|---|---|
| NumPy-heavy loops | **Numba @njit** |
| Array operations without loops | **NumPy vectorization** (no Numba needed) |
| GPU computation | **Numba CUDA** or CuPy |
| General Python optimization | **Cython** |
| New high-perf module | **Rust (PyO3)** |
| Existing C library | **ctypes/cffi** |

---

## Practice Exercises

1. **Speed up a Monte Carlo simulation** (estimate π) using @njit.
2. **Use `parallel=True`** with `prange` and measure multi-core speedup.
3. **Write a @vectorize** function for a custom mathematical operation.
4. **Write a CUDA kernel** for element-wise array operations.
5. **Compare performance**: pure Python vs NumPy vs Numba for the same algorithm.
6. **Profile** a Numba function with `%timeit` and inspect the generated LLVM IR.
